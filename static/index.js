let myChart;

// on page load fetch the data
fetch(`/data`)
  .then((response) => response.json())
  .then((data) => {
    // get the labels and data from the response
    const labels = data.years;

    let gistemp = data.giss;
    let ghcn = data.ghcn;
    let crutem = data.crutem;

    // Check if the chart is already created and delete if it is
    if (myChart) {
      myChart.destroy();
    }
    // Create a new chart
    const ctx = document.getElementById("myChart").getContext("2d");
    myChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "GISTEMP",
            data: gistemp,
            fill: false,
            borderColor: "rgb(255, 99, 132)",
            tension: 0.1,
          },
          {
            label: "GHCN",
            data: ghcn,
            fill: false,
            borderColor: "rgb(54, 162, 235)",
            tension: 0.1,
          },
          {
            label: "CRUTEM",
            data: crutem,
            fill: false,
            borderColor: "rgb(75, 192, 192)",
            tension: 0.1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
  });
