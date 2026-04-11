const numberFormat = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2,
});

const compactNumberFormat = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 3,
  minimumFractionDigits: 3,
});

const presets = {
  baseline: {
    spotPrice: 100,
    strikePrice: 100,
    daysToExpiry: 365,
    riskFreeRate: 4.5,
    volatility: 20,
  },
  momentum: {
    spotPrice: 185,
    strikePrice: 200,
    daysToExpiry: 180,
    riskFreeRate: 4.35,
    volatility: 34,
  },
  hedge: {
    spotPrice: 102,
    strikePrice: 95,
    daysToExpiry: 120,
    riskFreeRate: 4.1,
    volatility: 18,
  },
  earnings: {
    spotPrice: 160,
    strikePrice: 165,
    daysToExpiry: 21,
    riskFreeRate: 4.6,
    volatility: 72,
  },
};

const state = {
  sensitivityDriver: "spot",
};

const elements = {
  form: document.getElementById("pricing-form"),
  validationMessage: document.getElementById("validation-message"),
  inputs: {
    spotPrice: document.getElementById("spot-price"),
    strikePrice: document.getElementById("strike-price"),
    daysToExpiry: document.getElementById("days-to-expiry"),
    riskFreeRate: document.getElementById("risk-free-rate"),
    volatility: document.getElementById("volatility"),
  },
  metrics: {
    call: document.getElementById("metric-call"),
    put: document.getElementById("metric-put"),
    moneyness: document.getElementById("metric-moneyness"),
  },
  call: {
    price: document.getElementById("call-price"),
    intrinsic: document.getElementById("call-intrinsic"),
    timeValue: document.getElementById("call-time-value"),
    breakeven: document.getElementById("call-breakeven"),
  },
  put: {
    price: document.getElementById("put-price"),
    intrinsic: document.getElementById("put-intrinsic"),
    timeValue: document.getElementById("put-time-value"),
    breakeven: document.getElementById("put-breakeven"),
  },
  greeks: {
    callDelta: document.getElementById("call-delta"),
    putDelta: document.getElementById("put-delta"),
    callGamma: document.getElementById("call-gamma"),
    putGamma: document.getElementById("put-gamma"),
    callTheta: document.getElementById("call-theta"),
    putTheta: document.getElementById("put-theta"),
    callVega: document.getElementById("call-vega"),
    putVega: document.getElementById("put-vega"),
    callRho: document.getElementById("call-rho"),
    putRho: document.getElementById("put-rho"),
  },
  insightList: document.getElementById("insight-list"),
  payoffChart: document.getElementById("payoff-chart"),
  sensitivityChart: document.getElementById("sensitivity-chart"),
};

function erf(x) {
  const sign = Math.sign(x);
  const value = Math.abs(x);
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;
  const t = 1 / (1 + p * value);
  const polynomial =
    (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t;
  const y = 1 - polynomial * Math.exp(-value * value);
  return sign * y;
}

function normalCdf(x) {
  return 0.5 * (1 + erf(x / Math.SQRT2));
}

function normalPdf(x) {
  return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
}

function blackScholesPrice({ spotPrice, strikePrice, timeToExpiry, riskFreeRate, volatility, optionType }) {
  const sqrtT = Math.sqrt(timeToExpiry);
  const d1 =
    (Math.log(spotPrice / strikePrice) +
      (riskFreeRate + (volatility * volatility) / 2) * timeToExpiry) /
    (volatility * sqrtT);
  const d2 = d1 - volatility * sqrtT;

  if (optionType === "call") {
    return spotPrice * normalCdf(d1) - strikePrice * Math.exp(-riskFreeRate * timeToExpiry) * normalCdf(d2);
  }

  return strikePrice * Math.exp(-riskFreeRate * timeToExpiry) * normalCdf(-d2) - spotPrice * normalCdf(-d1);
}

function calculateGreeks({ spotPrice, strikePrice, timeToExpiry, riskFreeRate, volatility, optionType }) {
  const sqrtT = Math.sqrt(timeToExpiry);
  const d1 =
    (Math.log(spotPrice / strikePrice) +
      (riskFreeRate + (volatility * volatility) / 2) * timeToExpiry) /
    (volatility * sqrtT);
  const d2 = d1 - volatility * sqrtT;

  const gamma = normalPdf(d1) / (spotPrice * volatility * sqrtT);
  const vega = spotPrice * sqrtT * normalPdf(d1);

  if (optionType === "call") {
    return {
      delta: normalCdf(d1),
      gamma,
      theta:
        (-spotPrice * normalPdf(d1) * volatility) / (2 * sqrtT) -
        riskFreeRate * strikePrice * Math.exp(-riskFreeRate * timeToExpiry) * normalCdf(d2),
      vega,
      rho: strikePrice * timeToExpiry * Math.exp(-riskFreeRate * timeToExpiry) * normalCdf(d2),
    };
  }

  return {
    delta: normalCdf(d1) - 1,
    gamma,
    theta:
      (-spotPrice * normalPdf(d1) * volatility) / (2 * sqrtT) +
      riskFreeRate * strikePrice * Math.exp(-riskFreeRate * timeToExpiry) * normalCdf(-d2),
    vega,
    rho: -strikePrice * timeToExpiry * Math.exp(-riskFreeRate * timeToExpiry) * normalCdf(-d2),
  };
}

function formatCurrency(value) {
  return `$${numberFormat.format(value)}`;
}

function formatSignedCurrency(value) {
  return `${value < 0 ? "-" : ""}$${numberFormat.format(Math.abs(value))}`;
}

function formatDecimal(value) {
  return compactNumberFormat.format(value);
}

function clampValue(value, min) {
  return Math.max(Number(value), min);
}

function getInputs() {
  return {
    spotPrice: clampValue(elements.inputs.spotPrice.value, 0.01),
    strikePrice: clampValue(elements.inputs.strikePrice.value, 0.01),
    daysToExpiry: clampValue(elements.inputs.daysToExpiry.value, 1),
    riskFreeRate: Number(elements.inputs.riskFreeRate.value),
    volatility: clampValue(elements.inputs.volatility.value, 0.01),
  };
}

function validateInputs({ spotPrice, strikePrice, daysToExpiry, volatility }) {
  if (spotPrice <= 0 || strikePrice <= 0) {
    return "Spot and strike must both be positive.";
  }

  if (daysToExpiry <= 0) {
    return "Days to expiry must be greater than zero.";
  }

  if (volatility <= 0) {
    return "Volatility must be greater than zero.";
  }

  return "";
}

function generateSequence(start, end, count) {
  const result = [];
  const step = (end - start) / (count - 1);

  for (let index = 0; index < count; index += 1) {
    result.push(start + step * index);
  }

  return result;
}

function computeModel() {
  const raw = getInputs();
  const validationMessage = validateInputs(raw);
  elements.validationMessage.textContent = validationMessage;

  const modelInputs = {
    spotPrice: raw.spotPrice,
    strikePrice: raw.strikePrice,
    timeToExpiry: raw.daysToExpiry / 365,
    riskFreeRate: raw.riskFreeRate / 100,
    volatility: raw.volatility / 100,
  };

  const callPrice = blackScholesPrice({ ...modelInputs, optionType: "call" });
  const putPrice = blackScholesPrice({ ...modelInputs, optionType: "put" });
  const callGreeks = calculateGreeks({ ...modelInputs, optionType: "call" });
  const putGreeks = calculateGreeks({ ...modelInputs, optionType: "put" });

  const callIntrinsic = Math.max(raw.spotPrice - raw.strikePrice, 0);
  const putIntrinsic = Math.max(raw.strikePrice - raw.spotPrice, 0);

  return {
    raw,
    modelInputs,
    validationMessage,
    callPrice,
    putPrice,
    callIntrinsic,
    putIntrinsic,
    callTimeValue: callPrice - callIntrinsic,
    putTimeValue: putPrice - putIntrinsic,
    callGreeks,
    putGreeks,
    moneyness: raw.spotPrice / raw.strikePrice,
  };
}

function payoffSeries({ raw, callPrice, putPrice }) {
  const floor = Math.max(raw.spotPrice * 0.45, 1);
  const ceiling = raw.spotPrice * 1.65;
  const prices = generateSequence(floor, ceiling, 44);

  return {
    xLabel: "Underlying Price at Expiry",
    yLabel: "P/L",
    legend: [
      { color: "#cf6b2a", label: "Long Call" },
      { color: "#1c6a73", label: "Long Put" },
    ],
    currentMarker: raw.spotPrice,
    strikeMarker: raw.strikePrice,
    series: [
      {
        color: "#cf6b2a",
        label: "Long Call",
        data: prices.map((price) => ({
          x: price,
          y: Math.max(price - raw.strikePrice, 0) - callPrice,
        })),
      },
      {
        color: "#1c6a73",
        label: "Long Put",
        data: prices.map((price) => ({
          x: price,
          y: Math.max(raw.strikePrice - price, 0) - putPrice,
        })),
      },
    ],
  };
}

function sensitivitySeries(model) {
  const { raw, modelInputs } = model;
  let driverLabel = "Spot Price";
  let xValues = [];

  if (state.sensitivityDriver === "volatility") {
    driverLabel = "Volatility";
    xValues = generateSequence(Math.max(raw.volatility * 0.45, 5), Math.max(raw.volatility * 1.75, 35), 44);
  } else if (state.sensitivityDriver === "time") {
    driverLabel = "Days to Expiry";
    xValues = generateSequence(7, Math.max(raw.daysToExpiry * 1.9, 120), 44);
  } else {
    xValues = generateSequence(Math.max(raw.spotPrice * 0.55, 1), raw.spotPrice * 1.55, 44);
  }

  const series = xValues.map((value) => {
    if (state.sensitivityDriver === "volatility") {
      return {
        x: value,
        call: blackScholesPrice({
          ...modelInputs,
          volatility: value / 100,
          optionType: "call",
        }),
        put: blackScholesPrice({
          ...modelInputs,
          volatility: value / 100,
          optionType: "put",
        }),
      };
    }

    if (state.sensitivityDriver === "time") {
      return {
        x: value,
        call: blackScholesPrice({
          ...modelInputs,
          timeToExpiry: value / 365,
          optionType: "call",
        }),
        put: blackScholesPrice({
          ...modelInputs,
          timeToExpiry: value / 365,
          optionType: "put",
        }),
      };
    }

    return {
      x: value,
      call: blackScholesPrice({
        ...modelInputs,
        spotPrice: value,
        optionType: "call",
      }),
      put: blackScholesPrice({
        ...modelInputs,
        spotPrice: value,
        optionType: "put",
      }),
    };
  });

  return {
    xLabel: driverLabel,
    yLabel: "Option Value",
    legend: [
      { color: "#cf6b2a", label: "Call Value" },
      { color: "#1c6a73", label: "Put Value" },
    ],
    currentMarker:
      state.sensitivityDriver === "volatility"
        ? raw.volatility
        : state.sensitivityDriver === "time"
          ? raw.daysToExpiry
          : raw.spotPrice,
    series: [
      {
        color: "#cf6b2a",
        label: "Call Value",
        data: series.map((point) => ({ x: point.x, y: point.call })),
      },
      {
        color: "#1c6a73",
        label: "Put Value",
        data: series.map((point) => ({ x: point.x, y: point.put })),
      },
    ],
  };
}

function describeInsights(model) {
  const { raw, callPrice, putPrice, callGreeks, putGreeks, moneyness } = model;
  const views = [];

  if (Math.abs(moneyness - 1) < 0.03) {
    views.push("The contract is near-the-money, so delta is responsive and gamma is carrying the short-horizon convexity.");
  } else if (moneyness > 1) {
    views.push("Spot sits above strike, which supports the call's intrinsic value and compresses the put's relevance.");
  } else {
    views.push("Spot sits below strike, so the put carries more protection value while the call remains mostly optionality.");
  }

  if (raw.daysToExpiry < 45) {
    views.push("Short tenor makes theta visible. Time decay is now a meaningful daily headwind unless realized moves exceed expectation.");
  } else {
    views.push("Longer tenor leaves more value in optionality, so vega matters more than day-to-day theta noise.");
  }

  if (raw.volatility > 45) {
    views.push("High volatility is inflating both premiums. This setup is more about paying for convexity than harvesting cheap exposure.");
  } else {
    const leadingSide = callPrice > putPrice ? "call" : "put";
    const leadingDelta = Math.abs(callGreeks.delta) > Math.abs(putGreeks.delta) ? "directional call exposure" : "downside put exposure";
    views.push(`Lower volatility keeps premiums tighter, so the ${leadingSide} side looks cleaner if the trade thesis is mostly ${leadingDelta}.`);
  }

  return views;
}

function buildPath(points, bounds) {
  const { minX, maxX, minY, maxY, width, height, padding } = bounds;

  return points
    .map((point, index) => {
      const x = padding.left + ((point.x - minX) / (maxX - minX || 1)) * (width - padding.left - padding.right);
      const y = height - padding.bottom - ((point.y - minY) / (maxY - minY || 1)) * (height - padding.top - padding.bottom);
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

function renderChart(container, config) {
  const width = 680;
  const height = 320;
  const padding = { top: 16, right: 24, bottom: 36, left: 56 };
  const allPoints = config.series.flatMap((entry) => entry.data);
  const xValues = allPoints.map((point) => point.x);
  const yValues = allPoints.map((point) => point.y);
  const minX = Math.min(...xValues);
  const maxX = Math.max(...xValues);
  let minY = Math.min(...yValues);
  let maxY = Math.max(...yValues);

  if (minY === maxY) {
    minY -= 1;
    maxY += 1;
  }

  const spanY = maxY - minY;
  minY -= spanY * 0.12;
  maxY += spanY * 0.12;

  const bounds = { minX, maxX, minY, maxY, width, height, padding };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const gridRows = 5;
  const gridCols = 5;
  const zeroY =
    minY <= 0 && maxY >= 0
      ? height - padding.bottom - ((0 - minY) / (maxY - minY || 1)) * innerHeight
      : null;

  let svg = `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${config.yLabel} versus ${config.xLabel}">`;

  for (let row = 0; row <= gridRows; row += 1) {
    const y = padding.top + (innerHeight / gridRows) * row;
    svg += `<line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="rgba(23,35,43,0.10)" stroke-width="1" />`;
    const tickValue = maxY - ((maxY - minY) / gridRows) * row;
    svg += `<text x="${padding.left - 10}" y="${y + 4}" text-anchor="end" fill="#5f6b71" font-size="11" font-family="IBM Plex Mono">${numberFormat.format(tickValue)}</text>`;
  }

  for (let col = 0; col <= gridCols; col += 1) {
    const x = padding.left + (innerWidth / gridCols) * col;
    svg += `<line x1="${x}" y1="${padding.top}" x2="${x}" y2="${height - padding.bottom}" stroke="rgba(23,35,43,0.08)" stroke-width="1" />`;
    const tickValue = minX + ((maxX - minX) / gridCols) * col;
    svg += `<text x="${x}" y="${height - padding.bottom + 20}" text-anchor="middle" fill="#5f6b71" font-size="11" font-family="IBM Plex Mono">${numberFormat.format(tickValue)}</text>`;
  }

  if (zeroY !== null) {
    svg += `<line x1="${padding.left}" y1="${zeroY}" x2="${width - padding.right}" y2="${zeroY}" stroke="rgba(23,35,43,0.28)" stroke-width="1.2" />`;
  }

  if (typeof config.currentMarker === "number") {
    const markerX =
      padding.left + ((config.currentMarker - minX) / (maxX - minX || 1)) * innerWidth;
    svg += `<line x1="${markerX}" y1="${padding.top}" x2="${markerX}" y2="${height - padding.bottom}" stroke="rgba(23,35,43,0.24)" stroke-dasharray="6 6" stroke-width="1.4" />`;
  }

  if (typeof config.strikeMarker === "number") {
    const strikeX =
      padding.left + ((config.strikeMarker - minX) / (maxX - minX || 1)) * innerWidth;
    svg += `<line x1="${strikeX}" y1="${padding.top}" x2="${strikeX}" y2="${height - padding.bottom}" stroke="rgba(207,107,42,0.44)" stroke-dasharray="4 8" stroke-width="1.2" />`;
  }

  config.series.forEach((entry) => {
    const path = buildPath(entry.data, bounds);
    svg += `<path d="${path}" fill="none" stroke="${entry.color}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" />`;
  });

  svg += `<text x="${width / 2}" y="${height - 4}" text-anchor="middle" fill="#5f6b71" font-size="12" font-family="IBM Plex Mono">${config.xLabel}</text>`;
  svg += `<text transform="translate(16 ${height / 2}) rotate(-90)" text-anchor="middle" fill="#5f6b71" font-size="12" font-family="IBM Plex Mono">${config.yLabel}</text>`;
  svg += "</svg>";

  const legend = config.legend
    .map(
      (item) => `
        <span class="legend-item">
          <span class="legend-swatch" style="background:${item.color}"></span>
          <span>${item.label}</span>
        </span>
      `
    )
    .join("");

  container.innerHTML = `
    <div class="chart-shell">
      ${svg}
      <div class="chart-meta">
        <div class="chart-legend">${legend}</div>
        <span>${config.currentMarker ? "Dashed line marks current input" : ""}</span>
      </div>
    </div>
  `;
}

function updateView() {
  const model = computeModel();

  elements.metrics.call.textContent = formatCurrency(model.callPrice);
  elements.metrics.put.textContent = formatCurrency(model.putPrice);
  elements.metrics.moneyness.textContent = `${compactNumberFormat.format(model.moneyness)}x`;

  elements.call.price.textContent = formatCurrency(model.callPrice);
  elements.call.intrinsic.textContent = formatCurrency(model.callIntrinsic);
  elements.call.timeValue.textContent = formatCurrency(model.callTimeValue);
  elements.call.breakeven.textContent = formatCurrency(model.raw.strikePrice + model.callPrice);

  elements.put.price.textContent = formatCurrency(model.putPrice);
  elements.put.intrinsic.textContent = formatCurrency(model.putIntrinsic);
  elements.put.timeValue.textContent = formatCurrency(model.putTimeValue);
  elements.put.breakeven.textContent = formatCurrency(model.raw.strikePrice - model.putPrice);

  elements.greeks.callDelta.textContent = formatDecimal(model.callGreeks.delta);
  elements.greeks.putDelta.textContent = formatDecimal(model.putGreeks.delta);
  elements.greeks.callGamma.textContent = formatDecimal(model.callGreeks.gamma);
  elements.greeks.putGamma.textContent = formatDecimal(model.putGreeks.gamma);
  elements.greeks.callTheta.textContent = formatSignedCurrency(model.callGreeks.theta / 365);
  elements.greeks.putTheta.textContent = formatSignedCurrency(model.putGreeks.theta / 365);
  elements.greeks.callVega.textContent = formatCurrency(model.callGreeks.vega / 100);
  elements.greeks.putVega.textContent = formatCurrency(model.putGreeks.vega / 100);
  elements.greeks.callRho.textContent = formatSignedCurrency(model.callGreeks.rho / 100);
  elements.greeks.putRho.textContent = formatSignedCurrency(model.putGreeks.rho / 100);

  const insights = describeInsights(model);
  elements.insightList.innerHTML = insights.map((text) => `<li>${text}</li>`).join("");

  renderChart(elements.payoffChart, payoffSeries(model));
  renderChart(elements.sensitivityChart, sensitivitySeries(model));
}

function applyPreset(presetName) {
  const preset = presets[presetName];

  if (!preset) {
    return;
  }

  Object.entries(preset).forEach(([key, value]) => {
    elements.inputs[key].value = value;
  });

  document.querySelectorAll(".preset-chip").forEach((button) => {
    button.classList.toggle("active", button.dataset.preset === presetName);
  });

  updateView();
}

elements.form.addEventListener("input", () => {
  document.querySelectorAll(".preset-chip").forEach((button) => button.classList.remove("active"));
  updateView();
});

document.querySelectorAll(".preset-chip").forEach((button) => {
  button.addEventListener("click", () => applyPreset(button.dataset.preset));
});

document.querySelectorAll(".segment").forEach((button) => {
  button.addEventListener("click", () => {
    state.sensitivityDriver = button.dataset.driver;

    document.querySelectorAll(".segment").forEach((segment) => {
      segment.classList.toggle("active", segment === button);
    });

    updateView();
  });
});

applyPreset("baseline");
