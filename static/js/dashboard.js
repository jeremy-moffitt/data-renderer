const datasetSelect = document.querySelector("#dataset-select");
const filterControls = document.querySelector("#filter-controls");
const description = document.querySelector("#dataset-description");
const status = document.querySelector("#status");
const chartArea = document.querySelector("#chart-area");
const chartTitle = document.querySelector("#chart-title");
const svg = document.querySelector("#line-chart");

const svgNamespace = "http://www.w3.org/2000/svg";
let requestSequence = 0;
let currentFilters = [];

function appendSvgElement(parent, name, attributes = {}, text = "") {
  const element = document.createElementNS(svgNamespace, name);
  for (const [key, value] of Object.entries(attributes)) {
    element.setAttribute(key, value);
  }
  if (text) element.textContent = text;
  parent.append(element);
  return element;
}

function renderLineChart(chart) {
  const width = 960;
  const height = 490;
  const left = 72;
  const right = 930;
  const top = 24;
  const bottom = 390;
  const yMin = chart.yAxis.min;
  const yMax = chart.yAxis.max;
  const yRange = yMax - yMin;
  const x = (index) => left + (chart.labels.length < 2
    ? 0
    : index * (right - left) / (chart.labels.length - 1));
  const y = (value) => bottom - ((value - yMin) / yRange) * (bottom - top);
  const formatY = (value) => chart.yAxis.format === "percent"
    ? `${Math.round(value * 100)}%`
    : `${Number(value.toFixed(2))}`;

  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("aria-label", `${chart.title} line chart`);

  appendSvgElement(svg, "text", {
    x: 18,
    y: (top + bottom) / 2,
    transform: `rotate(-90 18 ${(top + bottom) / 2})`,
    class: "axis-label",
    "text-anchor": "middle",
  }, chart.yAxis.label);

  for (let tick = 0; tick <= 5; tick += 1) {
    const value = yMin + yRange * tick / 5;
    const lineY = y(value);
    appendSvgElement(svg, "line", {
      x1: left,
      x2: right,
      y1: lineY,
      y2: lineY,
      class: "grid-line",
    });
    appendSvgElement(svg, "text", {
      x: left - 12,
      y: lineY + 4,
      class: "tick-label",
      "text-anchor": "end",
    }, formatY(value));
  }

  appendSvgElement(svg, "line", {
    x1: left,
    x2: right,
    y1: bottom,
    y2: bottom,
    class: "axis-line",
  });

  const labelStep = Math.max(1, Math.ceil(chart.labels.length / 12));
  chart.labels.forEach((label, index) => {
    if (index % labelStep !== 0 && index !== chart.labels.length - 1) return;
    appendSvgElement(svg, "text", {
      x: x(index),
      y: bottom + 22,
      class: "tick-label",
      "text-anchor": "middle",
    }, label);
  });

  appendSvgElement(svg, "text", {
    x: (left + right) / 2,
    y: bottom + 53,
    class: "axis-label",
    "text-anchor": "middle",
  }, chart.xAxis.label);

  chart.series.forEach((series) => {
    const points = series.values
      .map((value, index) => `${x(index)},${y(value)}`)
      .join(" ");
    appendSvgElement(svg, "polyline", {
      points,
      fill: "none",
      stroke: series.color,
      class: "series-line",
    });
    series.values.forEach((value, index) => {
      const point = appendSvgElement(svg, "circle", {
        cx: x(index),
        cy: y(value),
        r: 3.5,
        fill: series.color,
        class: "series-point",
      });
      if (series.pointLabels && series.pointLabels[index]) {
        appendSvgElement(point, "title", {}, series.pointLabels[index]);
      }
    });
  });

  const legendY = 470;
  let legendX = left;
  chart.series.forEach((series) => {
    appendSvgElement(svg, "line", {
      x1: legendX,
      x2: legendX + 20,
      y1: legendY,
      y2: legendY,
      stroke: series.color,
      class: "legend-line",
    });
    appendSvgElement(svg, "text", {
      x: legendX + 27,
      y: legendY + 4,
      class: "legend-label",
    }, series.name);
    legendX += 27 + series.name.length * 8 + 34;
  });
}

async function loadDataset() {
  const sequence = ++requestSequence;
  const datasetId = datasetSelect.value;
  if (!datasetId) return;

  const query = new URLSearchParams();
  for (const filter of currentFilters) {
    query.set(filter.id, filter.select.value);
  }
  const suffix = query.size ? `?${query}` : "";
  status.textContent = "Loading chart…";
  chartArea.hidden = true;

  try {
    const response = await fetch(`/api/datasets/${encodeURIComponent(datasetId)}${suffix}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Unable to load this dataset.");
    if (sequence !== requestSequence) return;

    description.textContent = payload.description;
    currentFilters = payload.filters.map((filter) => {
      const label = document.createElement("label");
      label.className = "control";
      const labelText = document.createElement("span");
      labelText.textContent = filter.label;
      const select = document.createElement("select");
      select.setAttribute("aria-label", filter.label);
      select.replaceChildren(...filter.options.map((option) => {
        const element = document.createElement("option");
        element.value = option.value;
        element.textContent = option.label;
        element.selected = option.value === filter.value;
        return element;
      }));
      select.addEventListener("change", loadDataset);
      label.append(labelText, select);
      return { id: filter.id, select, label };
    });
    filterControls.replaceChildren(...currentFilters.map((filter) => filter.label));

    chartTitle.textContent = payload.chart.title;
    renderLineChart(payload.chart);
    chartArea.hidden = false;
    status.textContent = "";
  } catch (error) {
    if (sequence !== requestSequence) return;
    status.textContent = error.message;
  }
}

async function initialize() {
  try {
    const response = await fetch("/api/datasets");
    const datasets = await response.json();
    if (!response.ok) throw new Error("Unable to load available datasets.");
    if (!datasets.length) {
      status.textContent = "No datasets are registered yet.";
      return;
    }

    datasetSelect.replaceChildren(...datasets.map((dataset) => {
      const option = document.createElement("option");
      option.value = dataset.id;
      option.textContent = dataset.name;
      return option;
    }));
    datasetSelect.addEventListener("change", () => {
      currentFilters = [];
      filterControls.replaceChildren();
      loadDataset();
    });
    await loadDataset();
  } catch (error) {
    status.textContent = error.message;
  }
}

initialize();
