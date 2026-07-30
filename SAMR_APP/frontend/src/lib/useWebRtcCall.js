import { useEffect, useRef, useState } from "react";
import { GATEWAY_URL } from "./apiClient";

const STUN_SERVERS = [{ urls: "stun:stun.l.google.com:19302" }];

function wsUrl(roomId, token) {
  const base = GATEWAY_URL.replace(/^http/, "ws");
  return `${base}/signaling?room=${encodeURIComponent(roomId)}&token=${encodeURIComponent(token)}`;
}

/**
 * Videollamada WebRTC real contra la senalizacion de M4 (RF-13). No hay
 * TURN server: en redes con NAT restrictivo la conexion puede no
 * establecerse, algo esperable en un despliegue local de demostracion.
 */
export function useWebRtcCall({ roomId, token, localStream, isCaller, enabled }) {
  const [remoteStream, setRemoteStream] = useState(null);
  const [connectionState, setConnectionState] = useState("idle");
  const pcRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!enabled || !roomId || !token || !localStream) return undefined;

    let cancelled = false;
    const pc = new RTCPeerConnection({ iceServers: STUN_SERVERS });
    pcRef.current = pc;
    localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));

    pc.ontrack = (event) => {
      if (!cancelled) setRemoteStream(event.streams[0]);
    };
    pc.onconnectionstatechange = () => {
      if (!cancelled) setConnectionState(pc.connectionState);
    };

    const ws = new WebSocket(wsUrl(roomId, token));
    wsRef.current = ws;

    ws.onmessage = async (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "offer") {
        await pc.setRemoteDescription(new RTCSessionDescription(msg.sdp));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        ws.send(JSON.stringify({ type: "answer", sdp: answer }));
      } else if (msg.type === "answer") {
        await pc.setRemoteDescription(new RTCSessionDescription(msg.sdp));
      } else if (msg.type === "ice" && msg.candidate) {
        try {
          await pc.addIceCandidate(msg.candidate);
        } catch {
          // candidato tardio o duplicado, se ignora
        }
      }
    };

    pc.onicecandidate = (event) => {
      if (event.candidate && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "ice", candidate: event.candidate }));
      }
    };

    ws.onopen = async () => {
      setConnectionState("signaling");
      if (isCaller) {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        ws.send(JSON.stringify({ type: "offer", sdp: offer }));
      }
    };

    return () => {
      cancelled = true;
      ws.close();
      pc.close();
      pcRef.current = null;
      wsRef.current = null;
    };
  }, [enabled, roomId, token, localStream, isCaller]);

  return { remoteStream, connectionState };
}
