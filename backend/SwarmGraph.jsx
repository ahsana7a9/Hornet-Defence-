import * as d3 from "d3";
import { useEffect } from "react";

export default function SwarmGraph() {
  useEffect(() => {
    const svg = d3.select("#swarm");

    const nodes = [
      { id: "agent1" },
      { id: "agent2" },
      { id: "threat1" }
    ];

    const links = [
      { source: "agent1", target: "threat1" },
      { source: "agent2", target: "threat1" }
    ];

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id))
      .force("charge", d3.forceManyBody())
      .force("center", d3.forceCenter(300, 200));

    const link = svg.selectAll("line")
      .data(links)
      .enter().append("line")
      .attr("stroke", "yellow");

    const node = svg.selectAll("circle")
      .data(nodes)
      .enter().append("circle")
      .attr("r", 8)
      .attr("fill", "red");

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
    });

  }, []);

  return <svg id="swarm" width={600} height={400}></svg>;
}
