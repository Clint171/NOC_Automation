document.addEventListener('DOMContentLoaded', function () {
    fetch('/reports/monthly')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('monthlyChart');
            const labels = Object.keys(data.overall);
            const overallUptime = Object.values(data.overall);

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Overall Uptime (%)',
                        data: overallUptime,
                        borderWidth: 1,
                        borderColor: 'rgb(0, 47, 190)',
                        fill: true
                    }]
                },
                options: {
                    scales: {
                        
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        });
});