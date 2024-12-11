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
    this.shadowRoot.innerHTML = "";
    const items = document.createElement("div"); 
    const speaker_img = document.createElement("img"); 
    const speaker_src = this.getAttribute("speaker_src");
    if (speaker_src) {
      speaker_img.src = speaker_src;
      items.appendChild(speaker_img);
    }
    JSON.parse(lines).forEach(line => {
      const el = document.createElement("div"); 
      const text_el = document.createElement("span");
      const start_el = document.createElement("span");
      start_el.innerText = Math.round(line.start_time);
      const special_effect = /^\[.*\]$/;
      text_el.innerText = line.text;
      if (special_effect.test(line.text)) {
        text_el.className = "nonlinguistic";
      }
      el.appendChild(start_el);
      el.appendChild(text_el);
      items.appendChild(el);
    })
    if (!lines || !JSON.parse(lines).length) {
      const title = document.createElement("h3"); 
      title.innerText = "Generating Transcript...";
      this.shadowRoot.appendChild(title);
    }
    else {
      this.shadowRoot.appendChild(items);
    }
  }

  attributeChangedCallback(key, _, value) {
    if (key == "lines") {
      this.render();
    }
  }

}

export { LineList };
