import StyleGlobal from "style-global" with { type: "css" };
import StyleLineList from "style-line-list" with { type: "css" };
import { get_sum } from "api";

class LineList extends HTMLElement {

  static observedAttributes = ["lines"];

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
    const lines = this.getAttribute("lines").split(" ");
    const items = document.createElement("div"); 
    lines.forEach(line => {
      const el = document.createElement("div"); 
      el.innerText = line;
      items.appendChild(el);
    })
    const title = document.createElement("h3"); 
    title.innerText = "Summed via Server API...";
    const result_el = document.createElement("div"); 
    try {
      result_el.innerText = "Total = " + (await get_sum(
        "http://localhost:7777/api", lines
      ));
    }
    catch {
      result_el.innerText = "Connection Error!";
    }
    this.shadowRoot.innerHTML = "";
    this.shadowRoot.appendChild(items);
    this.shadowRoot.appendChild(title);
    this.shadowRoot.appendChild(result_el);
  }

  attributeChangedCallback(key, _, value) {
    if (key == "lines") {
      this.render();
    }
  }

}

export { LineList };
