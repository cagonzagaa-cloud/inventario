document.addEventListener('DOMContentLoaded', function () {
    const grafico = document.getElementById('graficoInventario');
    const circular = document.getElementById('graficoCircular');

    const dashboardDataNode = document.getElementById('dashboard-data');
    const distributionDataNode = document.getElementById('distribution-data');

    if (grafico && dashboardDataNode) {
        const dashboardData = JSON.parse(dashboardDataNode.textContent);

        new Chart(grafico, {
            type: 'line',
            data: {
                labels: dashboardData.labels,
                datasets: [
                    {
                        label: 'Entradas',
                        data: dashboardData.entradas,
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.15)',
                        tension: 0.35,
                        fill: true,
                        pointRadius: 4
                    },
                    {
                        label: 'Salidas',
                        data: dashboardData.salidas,
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.15)',
                        tension: 0.35,
                        fill: true,
                        pointRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 10,
                        right: 10,
                        bottom: 0,
                        left: 0
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });
    }

    // Make movement rows clickable when they have a data-href attribute
    const movimientoRows = document.querySelectorAll('table.table tbody tr[data-href]');
    if (movimientoRows.length) {
        movimientoRows.forEach(row => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => {
                const href = row.dataset.href;
                if (href) window.location.href = href;
            });
        });
    }

    if (circular && distributionDataNode) {
        const distributionData = JSON.parse(distributionDataNode.textContent);

        new Chart(circular, {
            type: 'doughnut',
            data: {
                labels: distributionData.labels,
                datasets: [{
                    data: distributionData.data,
                    backgroundColor: [
                        '#0d6efd', '#198754', '#f4b400', '#dc3545', '#6c757d'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '55%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
});

