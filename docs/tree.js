// ── Colour scheme by node type ─────────────────────────────────────────────
const COLOR = {
  outcome:     { fill: "#dbeafe", stroke: "#3b82d4" },
  opportunity: { fill: "#ffedd5", stroke: "#f97316" },
  experiment:  { fill: "#dcfce7", stroke: "#22c55e" },
};

function nodeColor(type, part) {
  return (COLOR[type] || COLOR.experiment)[part];
}

// ── Dimensions ─────────────────────────────────────────────────────────────
const container = document.getElementById("tree-container");
let width  = container.clientWidth;
let height = container.clientHeight;

const svg = d3.select("#tree-container")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

const zoomGroup = svg.append("g");

// ── Zoom behaviour ─────────────────────────────────────────────────────────
const zoom = d3.zoom()
  .scaleExtent([0.1, 3])
  .on("zoom", (event) => {
    zoomGroup.attr("transform", event.transform);
  });

svg.call(zoom);

// Zoom controls
document.getElementById("btn-zoom-in").addEventListener("click", () => {
  svg.transition().duration(250).call(zoom.scaleBy, 1.4);
});
document.getElementById("btn-zoom-out").addEventListener("click", () => {
  svg.transition().duration(250).call(zoom.scaleBy, 0.7);
});
document.getElementById("btn-reset").addEventListener("click", () => {
  svg.transition().duration(400).call(zoom.transform, d3.zoomIdentity);
  centreTree();
});

// ── Tooltip helpers ────────────────────────────────────────────────────────
const tooltip  = document.getElementById("tooltip");
const ttTitle  = document.getElementById("tt-title");
const ttMeta   = document.getElementById("tt-meta");

function showTooltip(event, d) {
  const meta = d.data.meta || {};
  ttTitle.textContent = d.data.name;

  const lines = [];
  if (meta.metric)           lines.push("Metric: " + meta.metric);
  if (meta.time_horizon)     lines.push("Horizon: " + meta.time_horizon);
  if (meta.alignment)        lines.push("Alignment: " + meta.alignment);
  if (meta.evidence)         lines.push("Evidence: " + meta.evidence);
  if (meta.customer_segment) lines.push("Segment: " + meta.customer_segment);
  if (meta.experiment)       lines.push("Experiment: " + meta.experiment);
  if (meta.signal)           lines.push("Signal: " + meta.signal);
  if (meta.effort)           lines.push("Effort: " + meta.effort);

  ttMeta.textContent = lines.join(" · ");
  tooltip.style.opacity = "1";
  moveTooltip(event);
}

function moveTooltip(event) {
  const x = event.clientX + 14;
  const y = event.clientY + 14;
  tooltip.style.left = Math.min(x, window.innerWidth - 340) + "px";
  tooltip.style.top  = Math.min(y, window.innerHeight - 120) + "px";
}

function hideTooltip() {
  tooltip.style.opacity = "0";
}

// ── Tree layout ────────────────────────────────────────────────────────────
const NODE_SIZE_X = 220;
const NODE_SIZE_Y = 36;

let root;

function buildTree(data) {
  root = d3.hierarchy(data);
  root.descendants().forEach((d, i) => {
    d.id = i;
    d._children = d.children;
    if (d.depth >= 2) d.children = null;
  });
  update(root);
  centreTree();
}

function update(source) {
  const treeLayout = d3.tree().nodeSize([NODE_SIZE_Y, NODE_SIZE_X]);
  treeLayout(root);

  const nodes = root.descendants();
  const links = root.links();

  const link = zoomGroup.selectAll(".link")
    .data(links, d => d.target.id);

  link.enter()
    .insert("path", "g")
    .attr("class", "link")
    .attr("d", d3.linkHorizontal().x(d => d.y).y(d => d.x))
    .style("opacity", 0)
    .transition().duration(300)
    .style("opacity", 1);

  link.transition().duration(300)
    .attr("d", d3.linkHorizontal().x(d => d.y).y(d => d.x));

  link.exit()
    .transition().duration(200)
    .style("opacity", 0)
    .remove();

  const node = zoomGroup.selectAll(".node")
    .data(nodes, d => d.id);

  const nodeEnter = node.enter()
    .append("g")
    .attr("class", "node")
    .attr("transform", d => `translate(${source.y0 ?? source.y},${source.x0 ?? source.x})`)
    .style("opacity", 0)
    .on("click", (event, d) => {
      d.children = d.children ? null : d._children;
      update(d);
    })
    .on("mouseover", showTooltip)
    .on("mousemove", moveTooltip)
    .on("mouseout",  hideTooltip);

  nodeEnter.append("circle")
    .attr("r", 7)
    .attr("fill",   d => nodeColor(d.data.type, "fill"))
    .attr("stroke", d => nodeColor(d.data.type, "stroke"));

  nodeEnter.append("text")
    .attr("class", "label-bg")
    .attr("dy", "0.32em")
    .attr("x", d => d.children || d._children ? -12 : 12)
    .attr("text-anchor", d => d.children || d._children ? "end" : "start")
    .text(d => truncate(d.data.name, 42));

  nodeEnter.append("text")
    .attr("dy", "0.32em")
    .attr("x", d => d.children || d._children ? -12 : 12)
    .attr("text-anchor", d => d.children || d._children ? "end" : "start")
    .text(d => truncate(d.data.name, 42));

  nodeEnter.append("text")
    .attr("class", "collapse-indicator")
    .attr("dy", "0.32em")
    .attr("x", 0)
    .attr("text-anchor", "middle")
    .style("font-size", "9px")
    .style("fill", d => nodeColor(d.data.type, "stroke"))
    .style("pointer-events", "none");

  nodeEnter.transition().duration(300)
    .attr("transform", d => `translate(${d.y},${d.x})`)
    .style("opacity", 1);

  const nodeUpdate = node.merge(nodeEnter);

  nodeUpdate.transition().duration(300)
    .attr("transform", d => `translate(${d.y},${d.x})`);

  nodeUpdate.select("circle")
    .attr("fill",   d => nodeColor(d.data.type, "fill"))
    .attr("stroke", d => nodeColor(d.data.type, "stroke"));

  nodeUpdate.selectAll("text:not(.collapse-indicator)")
    .attr("x", d => d.children || d._children ? -12 : 12)
    .attr("text-anchor", d => d.children || d._children ? "end" : "start");

  nodeUpdate.select(".collapse-indicator")
    .text(d => d._children && !d.children ? "+" : "");

  node.exit()
    .transition().duration(200)
    .style("opacity", 0)
    .attr("transform", d => `translate(${source.y},${source.x})`)
    .remove();

  root.descendants().forEach(d => { d.x0 = d.x; d.y0 = d.y; });
}

function centreTree() {
  const bounds = zoomGroup.node().getBBox();
  if (!bounds.width) return;
  const scale = Math.min(
    0.9,
    Math.min(width / (bounds.width + 80), height / (bounds.height + 80))
  );
  const tx = (width  - bounds.width  * scale) / 2 - bounds.x * scale;
  const ty = (height - bounds.height * scale) / 2 - bounds.y * scale;
  svg.transition().duration(500)
    .call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
}

function truncate(str, n) {
  return str && str.length > n ? str.slice(0, n - 1) + "\u2026" : str;
}

// ── Load data ──────────────────────────────────────────────────────────────
fetch("tree_data.json")
  .then(r => {
    if (!r.ok) throw new Error("HTTP " + r.status);
    return r.json();
  })
  .then(data => {
    const meta = data.meta || {};
    const generated = data.generated_at
      ? new Date(data.generated_at).toLocaleString()
      : "N/A";
    document.getElementById("nav-meta").textContent =
      `${meta.metric || data.name} \u00b7 Generated ${generated}`;
    buildTree(data);
  })
  .catch(err => {
    console.error("Failed to load tree_data.json:", err);
    document.getElementById("error-msg").style.display = "block";
    document.getElementById("nav-meta").textContent = "No tree data loaded";
  });

// ── Resize handler ────────────────────────────────────────────────────────
window.addEventListener("resize", () => {
  width  = container.clientWidth;
  height = container.clientHeight;
  svg.attr("width", width).attr("height", height);
});
