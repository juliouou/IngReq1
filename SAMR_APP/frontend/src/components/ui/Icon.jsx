// Set minimo de iconos de linea (sin emojis), estilo consistente con el
// resto del sistema de diseno: trazo simple, color heredado del texto.
const PATHS = {
  home: "M3 11.5 12 4l9 7.5 M5 10v9.5a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V10",
  chat: "M4 5h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H9l-4 4v-4H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z",
  heart:
    "M12 20.5s-7.5-4.6-10-9.3C.4 7.9 2 4.5 5.4 4a4.6 4.6 0 0 1 6.6 2 4.6 4.6 0 0 1 6.6-2c3.4.5 5 3.9 3.4 7.2-2.5 4.7-10 9.3-10 9.3Z",
  video: "M3 7a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7Z M21 8.5 15 12l6 3.5v-7Z",
  shield: "M12 3l7 3v6c0 4.5-3 7.7-7 9-4-1.3-7-4.5-7-9V6l7-3Z",
  bell: "M6 9a6 6 0 0 1 12 0v5l1.8 2.5H4.2L6 14V9Z M9.5 19a2.5 2.5 0 0 0 5 0",
  bot: "M8 7V4h8v3 M5 7h14a1 1 0 0 1 1 1v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a1 1 0 0 1 1-1Z M9 12v2 M15 12v2 M2 10v4 M22 10v4",
  send: "M3 11.5 20.5 3 15 20.5l-4-7.5-8-1Z",
  mic: "M9 3a3 3 0 0 1 6 0v7a3 3 0 0 1-6 0V3Z M5 11a7 7 0 0 0 14 0 M12 18v3",
  "mic-off": "M9 3a3 3 0 0 1 6 0v7c0 .6-.13 1.16-.36 1.66 M5 11a7 7 0 0 0 10.24 6.2 M15.7 15.7A7 7 0 0 1 5 11 M12 18v3 M3 3l18 18",
  camera:
    "M4 8h2.5l1-2h9l1 2H20a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1Z M12 17a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z",
  x: "M6 6l12 12M18 6 6 18",
  menu: "M4 6h16 M4 12h16 M4 18h16",
  activity: "M3 12h4l2 8 4-16 2 8h6",
  thermometer:
    "M12 3a2 2 0 0 0-2 2v9.5a4 4 0 1 0 4 0V5a2 2 0 0 0-2-2Z M12 14v3",
};

export function Icon({ name, size = 16, strokeWidth = 2, style, ...rest }) {
  const d = PATHS[name];
  if (!d) return null;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={{ display: "block", flexShrink: 0, ...style }}
      {...rest}
    >
      <path d={d} />
    </svg>
  );
}
