import {fetchCounties, fetchDevices , fetchDeviceStatuses, fetchRegions} from "./requests.js";

document.addEventListener("DOMContentLoaded" , async ()=>{
    let deviceStatuses = await fetchDeviceStatuses();
    let devices = await fetchDevices()
    let counties = await fetchCounties();
    let regions = await fetchRegions();
    let consolidated = consolidateData(regions, counties, devices, deviceStatuses)

    // Devices pie chart
    let context= {
        "Devices up" : 0,
        "Devices down" : 0
    }
    for(let device in deviceStatuses){
        if(deviceStatuses[device].status == true){
            context["Devices up"]+=1;
        }
        else{
            context["Devices down"]+=1;
        }
    }

    const ctxDevice = document.getElementById('deviceAvailability');
    const deviceLabels = Object.keys(context);
    const deviceUptime = Object.values(context);

    new Chart(ctxDevice, {
        type: 'pie',
        data: {
            labels: deviceLabels,
            datasets: [{
                label: 'Devices Up',
                data: deviceUptime,
                backgroundColor : ['rgb(54, 162, 235)','rgb(255, 99, 132)'],
                hoverOffset: 4
            }]
        },
        options: {}
    });

    function renderCharts(consolidatedData) {
        // Extract data for Counties
        const countyLabels = [];
        const countyPercentages = [];
    
        consolidatedData.regions.forEach(region => {
            region.counties.forEach(county => {
                countyLabels.push(county.name);
                countyPercentages.push(county.percentageUp);
            });
        });
    
        // Extract data for Regions
        const regionLabels = consolidatedData.regions.map(region => region.name);
        const regionPercentages = consolidatedData.regions.map(region => region.percentageUp);
    
        // Get overall percentage
        const overallPercentageUp = consolidatedData.overallPercentageUp;
    
        // Create County Bar Chart
        new Chart(document.getElementById("countyAvailability"), {
            type: "bar",
            data: {
                labels: countyLabels,
                datasets: [{
                    label: "County Uptime (%)",
                    data: countyPercentages,
                    backgroundColor: "rgba(75, 192, 192, 0.6)",
                    borderColor: "rgba(75, 192, 192, 1)",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    
        // Create Region Bar Chart
        new Chart(document.getElementById("regionAvailability"), {
            type: "bar",
            data: {
                labels: regionLabels,
                datasets: [{
                    label: "Region Uptime (%)",
                    data: regionPercentages,
                    backgroundColor: "rgba(255, 159, 64, 0.6)",
                    borderColor: "rgba(255, 159, 64, 1)",
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    
        // Create Overall Pie Chart
        new Chart(document.getElementById("overallAvailability"), {
            type: "pie",
            data: {
                labels: ["Uptime (%)", "Downtime (%)"],
                datasets: [{
                    data: [overallPercentageUp, 100 - overallPercentageUp],
                    backgroundColor: ["#36A2EB", "#FF6384"]
                }]
            },
            options: {
                responsive: true
            }
        });
    }
    
    // Call the function after consolidating data
    renderCharts(consolidated);
    
})

function consolidateData(regions, counties, devices, deviceStatuses) {
    // Create lookup maps for quick access
    const regionMap = Object.fromEntries(regions.map(r => [r.id, { ...r, counties: [], percentageUp: 0 }]));
    const countyMap = Object.fromEntries(counties.map(c => [c.id, { ...c, devices: [], percentageUp: 0 }]));
    const deviceMap = Object.fromEntries(devices.map(d => [d.ip, { ...d, status: null }]));

    // Link deviceStatuses to devices
    deviceStatuses.forEach(status => {
        if (deviceMap[status.device_ip]) {
            deviceMap[status.device_ip].status = status.status; // status is boolean (true = up, false = down)
        }
    });

    // Link devices to counties
    devices.forEach(device => {
        if (countyMap[device.county_id]) {
            countyMap[device.county_id].devices.push(deviceMap[device.ip]);
        }
    });

    // Calculate county percentageUp
    Object.values(countyMap).forEach(county => {
        const totalDevices = county.devices.length;
        if (totalDevices > 0) {
            const upDevices = county.devices.filter(d => d.status === true).length;
            county.percentageUp = (upDevices / totalDevices) * 100;
        } else {
            county.percentageUp = 0; // No devices, so 0% uptime
        }
    });

    // Link counties to regions
    counties.forEach(county => {
        if (regionMap[county.region_id]) {
            regionMap[county.region_id].counties.push(countyMap[county.id]);
        }
    });

    // Calculate region percentageUp
    Object.values(regionMap).forEach(region => {
        const totalCounties = region.counties.length;
        if (totalCounties > 0) {
            const totalPercentage = region.counties.reduce((sum, c) => sum + c.percentageUp, 0);
            region.percentageUp = totalPercentage / totalCounties;
        } else {
            region.percentageUp = 0; // No counties, so 0% uptime
        }
    });

    // Calculate overall percentageUp
    const totalRegions = Object.keys(regionMap).length;
    const totalRegionPercentage = Object.values(regionMap).reduce((sum, r) => sum + r.percentageUp, 0);
    const overallPercentageUp = totalRegions > 0 ? totalRegionPercentage / totalRegions : 0;
    console.log({ regions: Object.values(regionMap), overallPercentageUp })
    return { regions: Object.values(regionMap), overallPercentageUp };
}