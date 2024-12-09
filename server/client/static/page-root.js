import StyleGlobal from "style-global" with { type: "css" };
import StylePageRoot from "style-page-root" with { type: "css" };

class PageRoot extends HTMLElement {

  static eventHandlerKeys = [
    "srt-pages/new"
  ];

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StylePageRoot
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const template = document.getElementById("page-root-view");
    this.shadowRoot.appendChild(template.content.cloneNode(true));
  }

  toEventHandler(key) {
    if (key === "srt-pages/new") {
      return ({ detail }) => {
        const { id } = detail;
        const old_page_data = this.shadowRoot.getElementById(id);
        const new_page_data = document.createElement("page-data");
        new_page_data.setAttribute("transcript_state", "");
        new_page_data.setAttribute("lines", "[]");
        new_page_data.setAttribute("clip_id", "0");
        new_page_data.setAttribute(
          "listing", old_page_data.getAttribute("listing")
        );
        this.shadowRoot.insertBefore(new_page_data, old_page_data);
      }
    }
  }

}

export { PageRoot };
