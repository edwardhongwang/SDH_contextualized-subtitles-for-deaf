import StyleGlobal from "style-global" with { type: "css" };
import StyleLineList from "style-line-list" with { type: "css" };

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
    const lines = this.getAttribute("lines");
    const items = document.createElement("div"); 
    JSON.parse(lines).forEach(line => {
      const el = document.createElement("div"); 
      el.innerText = line.text;
      items.appendChild(el);
    })
    const title = document.createElement("h3"); 
    if (!lines || !JSON.parse(lines).length) {
      title.innerText = "Generating Transcript...";
    }
    this.shadowRoot.innerHTML = "";
    this.shadowRoot.appendChild(items);
    this.shadowRoot.appendChild(title);
  }

  attributeChangedCallback(key, _, value) {
    if (key == "lines") {
      this.render();
    }
  }

}

export { LineList };
