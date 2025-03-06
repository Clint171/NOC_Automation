export async function fetchDeviceStatuses(){
    let response = await fetch("/device_statuses");
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
}

export async function fetchDevices(){
    let response = await fetch("/devices");
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
}

export async function fetchCounties(){
    let response = await fetch("/counties");
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
}

export async function fetchRegions(){
    let response = await fetch("/regions");
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
}

export async function fetchDailyReport(){
    let response = await fetch("/reports/daily");
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
}

export async function fetchMonthlyReport(){
    let response = await fetch("/reports/monthly");
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
}

export async function fetchYearlyReport(){
    let response = await fetch("/reports/yearly");
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
}