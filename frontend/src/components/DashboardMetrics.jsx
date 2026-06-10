export function DashboardMetrics({ metrics, contributors }) {
    return(
        <div className="space-y-8">
            {/* Métricas Globais */}
            <section>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Estatísticas da Rede</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {/* Card Nós */}
                    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
                        <p className="text-gray-600 text-sm font-medium">Contribuidores</p>
                        <p className="text-4xl font-bold text-blue-600 mt-2">{metrics.num_nodes}</p>
                        <p className="text-gray-500 text-xs mt-2">nós únicos na rede</p>
                    </div>

                    {/* Card Arestas */}
                    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
                        <p className="text-gray-600 text-sm font-medium">Interações</p>
                        <p className="text-4xl font-bold text-green-600 mt-2">{metrics.num_edges}</p>
                        <p className="text-gray-500 text-xs mt-2">arestas (colaborações)</p>
                    </div>

                    {/* Card Densidade */}
                    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
                        <p className="text-gray-600 text-sm font-medium">Densidade</p>
                        <p className="text-4xl font-bold text-purple-600 mt-2">
                            {(metrics.density * 100).toFixed(1)}%
                        </p>
                        <p className="text-gray-500 text-xs mt-2">interconexão da rede</p>
                    </div>

                    {/* Card Diâmetro */}
                    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-orange-500">
                        <p className="text-gray-600 text-sm font-medium">Diâmetro</p>
                        <p className="text-4xl font-bold text-orange-600 mt-2">
                            {metrics.diameter || 'N/A'}
                        </p>
                        <p className="text-gray-500 text-xs mt-2">distância máxima</p>
                    </div>
                </div>
            </section>

            {/* Ranking */}
            <section>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Top Contribuidores (por PageRank)</h2>
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">Posição</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">Nome</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">PageRank</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">In-Degree</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">Out-Degree</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">Betweenness</th>
                                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase">Comunidade</th>
                            </tr>
                        </thead>
                        <tbody>
                            {contributors.map((contrib, idx) => (
                                <tr 
                                    key={contrib.id} 
                                    className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                                >
                                    <td className="px-6 py-4">
                                        <span className="font-bold text-gray-900">#{idx + 1}</span>
                                    </td>
                                    <td className="px-6 py-4 font-medium text-gray-900">
                                        {contrib.id}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded">
                                            {(contrib.pagerank || 0).toFixed(4)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-gray-600 text-sm">
                                        {(contrib.in_degree || 0).toFixed(2)}
                                    </td>
                                    <td className="px-6 py-4 text-gray-600 text-sm">
                                        {(contrib.out_degree || 0).toFixed(2)}
                                    </td>
                                    <td className="px-6 py-4 text-gray-600 text-sm">
                                        {(contrib.betweenness || 0).toFixed(4)}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="px-2 py-1 bg-gray-200 text-gray-800 text-xs font-semibold rounded">
                                            {contrib.community || 0}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>

            {/* Info do Gephi */}
            <section className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-bold text-blue-900 mb-2">📊 Visualização Completa no Gephi</h3>
                <p className="text-blue-800 mb-4">
                    Para visualizar o grafo interativo com layout força-dirigida, cores por comunidade e controles avançados:
                </p>
                <ol className="text-blue-800 space-y-2 ml-4 list-decimal">
                    <li>Abra <code className="bg-white px-2 py-1 rounded">Gephi</code></li>
                    <li>Importe o arquivo <code className="bg-white px-2 py-1 rounded">data/outputs/collaboration_graph.gexf</code></li>
                    <li>Configure layout (Force Atlas 2) e cores (comunidades)</li>
                    <li>Analise padrões, clusters e nós centrais</li>
                </ol>
            </section>
        </div>
    );
}