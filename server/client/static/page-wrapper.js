import StyleGlobal from "style-global" with { type: "css" };
import StylePageWrapper from "style-page-wrapper" with { type: "css" };

class PageWrapper extends HTMLElement {

  static eventHandlerKeys = [
    "srt-pages/select", "srt-pages/new"
  ];

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StylePageWrapper
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const template = document.getElementById("page-wrapper-view");
    this.shadowRoot.appendChild(template.content.cloneNode(true));
  }

  toEventHandler(key) {
    if (key === "srt-pages/new") {
      return ({ detail }) => {
        const page_list = this.shadowRoot.querySelector("page-list");
        let page_root = this.shadowRoot.querySelector("page-root");
        if (!page_root) {
          page_root = document.createElement("page-root");
          this.shadowRoot.appendChild(page_root);
        }
        const { listing, clip_id } = detail;
        page_list.className = "hidden";
        page_list.removeAttribute("empty");
        page_root.createNewPage(listing, clip_id);
      }
    }
    if (key === "srt-pages/select") {
      return ({ detail }) => {
        const page_list = this.shadowRoot.querySelector("page-list");
        page_list.openOneListing(detail.listing);
        page_list.className = "";
      }
    }
  }

}

export { PageWrapper };
