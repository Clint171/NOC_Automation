import { fetchDailyReport } from "./requests.js";

let dailyReport;

document.addEventListener('DOMContentLoaded', async ()=>{
    dailyReport = await fetchDailyReport();
    createOverallGraph(dailyReport);
});

document.getElementById("reportArea").addEventListener("change" , ()=>{
    let reportEl = document.getElementById("reportArea");
    if(reportEl.value == "overall"){
        createOverallGraph(dailyReport);
    }
    else if(reportEl.value == "devices"){
        createDeviceGraphs(dailyReport);
    }
    else if(reportEl.value == "counties"){
        createCountyGraphs(dailyReport);
    }
    else if(reportEl.value == "regions"){
        createRegionGraphs(dailyReport);
    }
});

function createOverallGraph(report){
    let tab = document.createElement("div");
    let graphContainer = document.createElement("div");
    let canvas = document.createElement("canvas");
    
    tab.classList.add('graph-card');
    graphContainer.classList.add('chart-container');

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: Object.keys(report.overall),
            datasets: [{
                label: 'Overall Uptime (%)',
                data: Object.values(report.overall),
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

    graphContainer.appendChild(canvas);
    tab.appendChild(graphContainer);
    document.querySelector('.container').innerHTML = ``;
    document.querySelector('.container').appendChild(tab);
}

function createDeviceGraphs(report){
    document.querySelector('.container').innerHTML = ``;
    let deviceList = Object.keys(report.devices);
    console.log(deviceList);
    let count = 0;
    for(let i in report.devices){
        let tab = document.createElement("div");
        let graphContainer = document.createElement("div");
        let canvas = document.createElement("canvas");
        
        tab.classList.add('graph-card');
        graphContainer.classList.add('chart-container');

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: Object.keys(report.devices[i]),
                datasets: [{
                    label: `${deviceList[count]} Uptime (%)`,
                    data: Object.values(report.devices[i]),
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

        graphContainer.appendChild(canvas);
        tab.appendChild(graphContainer);
        document.querySelector('.container').appendChild(tab);
        count++;
    }
}

function createCountyGraphs(report){
    document.querySelector('.container').innerHTML = ``;
    let countyList = Object.keys(report.counties);
    let count = 0;
    for(let i in report.counties){
        let tab = document.createElement("div");
        let graphContainer = document.createElement("div");
        let canvas = document.createElement("canvas");
        
        tab.classList.add('graph-card');
        graphContainer.classList.add('chart-container');

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: Object.keys(report.counties[i]),
                datasets: [{
                    label: `${countyList[count]} Uptime (%)`,
                    data: Object.values(report.counties[i]),
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

        graphContainer.appendChild(canvas);
        tab.appendChild(graphContainer);
        document.querySelector('.container').appendChild(tab);
        count++;
    }
}

function createRegionGraphs(report){
    document.querySelector('.container').innerHTML = ``;
    let regionList = Object.keys(report.regions);
    let count = 0;
    for(let i in report.regions){
        let tab = document.createElement("div");
        let graphContainer = document.createElement("div");
        let canvas = document.createElement("canvas");
        
        tab.classList.add('graph-card');
        graphContainer.classList.add('chart-container');

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: Object.keys(report.regions[i]),
                datasets: [{
                    label: `${regionList[count]} Uptime (%)`,
                    data: Object.values(report.regions[i]),
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

        graphContainer.appendChild(canvas);
        tab.appendChild(graphContainer);
        document.querySelector('.container').appendChild(tab);
        count++;
    }
}