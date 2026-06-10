import { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000/api';

export function useGraphData() {
    const [contributors, setContributors] = useState(null);
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // busca grafo completo
                const graphRes = await fetch(`${API_URL}/graph`);
                if (!graphRes.ok) throw new Error('Grafo não encontrado');
                const graph = await graphRes.json();

                // métricas globais
                const metricsRes = await fetch(`${API_URL}/metrics`);
                if (!metricsRes.ok) throw new Error('Métricas não encontradas');
                const metricsData = await metricsRes.json();

                // ordena por PageRank decrescente
                const orderedContributors = (graph.nodes || [])
                    .sort((a, b) => (b.pagerank || 0) - (a.pagerank || 0));

                setContributors(orderedContributors);
                setMetrics(metricsData);
                setLoading(false);
            } catch (err) {
                setError(err.message);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return { contributors, metrics, loading, error };
}