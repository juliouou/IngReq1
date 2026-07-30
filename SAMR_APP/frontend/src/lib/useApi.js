import { useCallback, useEffect, useState } from "react";

/**
 * Ejecuta una llamada al Gateway y expone estados de carga/error/datos,
 * sin fabricar datos falsos cuando la peticion falla.
 */
export function useApiQuery(queryFn, deps = []) {
  const [state, setState] = useState({ status: "loading", data: null, error: null });

  const run = useCallback(() => {
    let cancelled = false;
    setState({ status: "loading", data: null, error: null });
    queryFn()
      .then((data) => {
        if (!cancelled) setState({ status: "success", data, error: null });
      })
      .catch((error) => {
        if (!cancelled) setState({ status: "error", data: null, error });
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => run(), [run]);

  return { ...state, refetch: run };
}

export function useApiMutation(mutationFn) {
  const [state, setState] = useState({ status: "idle", error: null });

  const mutate = useCallback(
    async (...args) => {
      setState({ status: "loading", error: null });
      try {
        const data = await mutationFn(...args);
        setState({ status: "success", error: null });
        return data;
      } catch (error) {
        setState({ status: "error", error });
        throw error;
      }
    },
    [mutationFn]
  );

  return { ...state, mutate };
}
