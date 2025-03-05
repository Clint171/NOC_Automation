document.addEventListener('DOMContentLoaded', function () {
    fetch('/device_statuses')
        .then(response => response.json())
        .then(data => {
            let context= {
                "Devices up" : 0,
                "Devices down" : 0
            }
            for(device in data){
                if(data[device].status == true){
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
        });
    
    fetch('/reports/daily')
        .then(response =>{response.json()})
        .then(data =>{
            
        })
});