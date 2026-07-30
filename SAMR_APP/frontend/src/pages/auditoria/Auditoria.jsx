import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import * as auditoriaApi from "../../lib/api/auditoria";
import { useApiQuery, useApiMutation } from "../../lib/useApi";
import { EmptyState, ErrorState, LoadingState } from "../../components/ui/StateBlock";

export function Auditoria() {
  const { token } = useAuth();
  const logsQuery = useApiQuery(() => auditoriaApi.listarLogs(token), [token]);
  const exportMutation = useApiMutation(() => auditoriaApi.exportarAuditoria(token));
  const [seleccionado, setSeleccionado] = useState(null);
  const [detalle, setDetalle] = useState({ status: "idle", data: null, error: null });

  const verDetalle = async (log) => {
    setSeleccionado(log.id);
    setDetalle({ status: "loading", data: null, error: null });
    try {
      const data = await auditoriaApi.obtenerLog(log.id, token);
      setDetalle({ status: "success", data, error: null });
    } catch (error) {
      setDetalle({ status: "error", data: null, error });
    }
  };

  return (
    <>
      
      <div className="audit-toolbar">
        <span className="pill pill-info">GET /audit/logs</span>
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn btn-outline btn-sm" onClick={logsQuery.refetch}>
            Actualizar
          </button>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => exportMutation.mutate()}
            disabled={exportMutation.status === "loading"}
          >
            {exportMutation.status === "loading" ? "Exportando..." : "Exportar reporte (PDF)"}
          </button>
        </div>
      </div>

      {exportMutation.status === "error" && (
        <div className="banner banner-error">{exportMutation.error.message}</div>
      )}
      {exportMutation.status === "success" && (
        <div className="banner banner-ok">Solicitud de exportacion enviada a POST /audit/export.</div>
      )}

      <div className="card" style={{ marginBottom: 20 }}>
        {logsQuery.status === "loading" && <LoadingState text="Consultando GET /audit/logs..." />}
        {logsQuery.status === "error" && (
          <ErrorState
            title="M5 - Auditoria aun no respondio"
            detail={logsQuery.error.message}
            onRetry={logsQuery.refetch}
          />
        )}
        {logsQuery.status === "success" &&
          (Array.isArray(logsQuery.data) && logsQuery.data.length > 0 ? (
            <div className="audit-table-wrap">
              <table className="audit-table">
                <thead>
                  <tr>
                    <th>Modulo</th>
                    <th>Actor</th>
                    <th>Accion</th>
                    <th>Fecha</th>
                    <th>Hash</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {logsQuery.data.map((log) => (
                    <tr key={log.id}>
                      <td>
                        <span className="pill pill-info">{log.modulo_origen}</span>
                      </td>
                      <td>{log.actor}</td>
                      <td>{log.accion}</td>
                      <td>{log.timestamp ? new Date(log.timestamp).toLocaleString() : "--"}</td>
                      <td>
                        <span className="audit-hash">{(log.hash || "").slice(0, 12)}...</span>
                      </td>
                      <td>
                        <button className="btn btn-outline btn-sm" onClick={() => verDetalle(log)}>
                          Ver
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState title="No hay registros de auditoria" detail="M5 respondio una lista vacia." />
          ))}
      </div>

      {seleccionado && (
        <div className="card">
          <div className="card-title">Detalle del log {seleccionado}</div>
          {detalle.status === "loading" && <LoadingState text="Consultando GET /audit/logs/{id}..." />}
          {detalle.status === "error" && (
            <ErrorState title="No se pudo cargar el detalle" detail={detalle.error.message} />
          )}
          {detalle.status === "success" && (
            <pre style={{ fontSize: 12, whiteSpace: "pre-wrap", margin: 0 }}>
              {JSON.stringify(detalle.data, null, 2)}
            </pre>
          )}
        </div>
      )}
    </>
  );
}
