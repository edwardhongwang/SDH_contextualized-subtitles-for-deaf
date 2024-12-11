import StyleGlobal from "style-global" with { type: "css" };
import StyleNestedList from "style-nested-list" with { type: "css" };

class NestedList extends HTMLElement {

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StyleNestedList
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const template = document.getElementById("nested-list-view");
    const copy = template.content.cloneNode(true);
    const summary_el = copy.querySelector("summary");
    const content_el = copy.querySelector("div");
    summary_el.innerHTML = this.getAttribute("label");
    const listing = this.getAttribute("listing");
    const clip_count = parseInt(
      this.getAttribute("clip_count")
    );
    [...new Array(clip_count).keys()].forEach(clip_id => {
      const info_el = document.createElement("nested-item");
      info_el.setAttribute("clip_id", clip_id);
      info_el.setAttribute("listing", listing);
      content_el.appendChild(info_el);
    });
    this.shadowRoot.appendChild(copy);
  }

  setOpenDescription(open) {
    const details_el = this.shadowRoot.querySelector("details");
    if (open) {
      return details_el.setAttribute("open", "");
    }
    details_el.removeAttribute("open");
  }
};

export { NestedList };
