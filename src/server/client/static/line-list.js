import StyleGlobal from "style-global" with { type: "css" };
import StyleLineList from "style-line-list" with { type: "css" };
import { get_sum } from "api";

class LineList extends HTMLElement {

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StyleLineList
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const lines = this.getAttribute("lines").split(" ");
    const items = document.createElement("div"); 
    lines.forEach(line => {
      const el = document.createElement("div"); 
      el.innerText = line;
      items.appendChild(el);
    })
    this.shadowRoot.appendChild(items);
    const title = document.createElement("h3"); 
    title.innerText = "Summed via Server API...";
    this.shadowRoot.appendChild(title);
    const el = document.createElement("div"); 
    try {
      el.innerText = "Total = " + (await get_sum(
        "http://localhost:7777/api", lines
      ));
    }
    catch {
      el.innerText = "Connection Error!";
    }
    this.shadowRoot.appendChild(el);
  }

}

export { LineList };
