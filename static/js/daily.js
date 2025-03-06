import { fetchDailyReport } from "./requests.js";

// document.addEventListener('DOMContentLoaded', function () {
//     fetch('/reports/daily')
//         .then(response => response.json())
//         .then(data => {
//             const ctx = document.getElementById('dailyChart');
//             const labels = Object.keys(data.overall);
//             const overallUptime = Object.values(data.overall);

//             new Chart(ctx, {
//                 type: 'line',
//                 data: {
//                     labels: labels,
//                     datasets: [{
//                         label: 'Overall Uptime (%)',
//                         data: overallUptime,
//                         borderWidth: 1,
//                         borderColor: 'rgb(0, 47, 190)',
//                         fill: true
//                     }]
//                 },
//                 options: {
//                     scales: {
                        
//                         y: {
//                             beginAtZero: true,
//                             max: 100
//                         }
//                     }
//                 }
//             });
//         });
// });

document.addEventListener('DOMContentLoaded', async ()=>{
    let report = await fetchDailyReport();
    let tabTemplate;
    
    console.log(report);
});