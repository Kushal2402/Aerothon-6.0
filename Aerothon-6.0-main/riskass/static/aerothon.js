const btn = document.getElementById('btn')
btn.addEventListener("click",function getRiskAssessment() {
    var latitude = document.getElementById('latitude').value;
    var longitude = document.getElementById('longitude').value;

    fetch('/risk_assessment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('riskLevel').innerText = 'Error: ' + data.error;
        } else {
            document.getElementById('riskLevel').innerText = 'Risk Level: ' + data.risk_level;
            displayWeatherData(data.weather_data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
})


function displayWeatherData(weatherData) {
    const table = document.getElementById('weatherTable');
    table.innerHTML = ''; // Clear existing rows

    for (const [param, value] of Object.entries(weatherData)) {
        const row = table.insertRow();
        const paramCell = row.insertCell(0);
        const valueCell = row.insertCell(1);
        paramCell.innerText = param.replace(/_/g, ' '); // Replace underscores with spaces
        valueCell.innerText = value;
    }
}

const button = document.querySelector()