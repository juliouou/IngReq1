// Bloque reutilizable para los 4 estados que debe manejar cada pantalla:
// carga, error, vacio y (opcionalmente) exito.
export function LoadingState({ text = "Cargando..." }) {
  return (
    <div className="state-block">
      <span className="spinner" role="status" aria-label="Cargando" />
      <span className="t">{text}</span>
    </div>
  );
}

export function ErrorState({ title = "Algo salio mal", detail, onRetry }) {
  return (
    <div className="state-block state-error">
      <span className="ic">!</span>
      <span className="t">{title}</span>
      {detail && <span className="s">{detail}</span>}
      {onRetry && (
        <button type="button" className="btn btn-outline btn-sm" onClick={onRetry}>
          Reintentar
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title = "Todavia no hay datos", detail }) {
  return (
    <div className="state-block">
      <span className="ic">--</span>
      <span className="t">{title}</span>
      {detail && <span className="s">{detail}</span>}
    </div>
  );
}
