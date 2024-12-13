import { PageWrapper } from "page-wrapper";
import { NestedItem } from "nested-item";
import { NestedList } from "nested-list";
import { PageList } from "page-list";
import { LineList } from "line-list";
import { PageRoot } from "page-root";
import { PageData } from "page-data";
import { PagePane } from "page-pane";
import { PageNav } from "page-nav";

const valid_events = new Set([
  "srt-pages/select",
  "srt-page/enrich",
  "srt-page/undo",
  "srt-pages/new"
])

const index = (user) => {
  // Wrapper
  customElements.define(
    "page-wrapper", eventReceiver(
      PageWrapper, PageWrapper.eventHandlerKeys
    )
  );
  // Pages
  customElements.define(
    "page-root", PageRoot
  );
  // Page
  customElements.define(
    "page-data", eventReceiver(
      PageData,
      PageData.eventHandlerKeys
    )
  );
  // Pane
  customElements.define(
    "page-pane", (
      inherit(PagePane, [
        "lines", "transcript_state", "id", "clip_id",
        "label", "source", "header", "figure_src",
        "speaker_src", "listing"
      ])
    )
  );
  // Subtitle lines
  customElements.define(
    "line-list", inherit(LineList, [
      "lines"
    ])
  )
  // Nav
  customElements.define(
    "page-nav", eventSender(PageNav)
  );
  customElements.define(
    'nested-item', eventSender(NestedItem)
  );
  customElements.define('nested-list', NestedList);
  customElements.define('page-list', PageList);
};


const eventSender = (element) => {
  return class extends element {
    sendCustomEvent(key, detail) {
      if (!valid_events.has(key)) {
        throw new Error(`Invalid Custom Event: "${key}"`);
      }
      const [bubbles, composed] = [true, true];
      this.shadowRoot.dispatchEvent(new CustomEvent(
        key, { detail, bubbles, composed }
      ));
    }
  }
}

const eventReceiver = (element, keys=[]) => {
  if (!keys.every(key => valid_events.has(key))) {
    throw new Error(`Invalid Custom Events`);
  }
  return class extends element {
    async connectedCallback() {
      await super.connectedCallback();
      keys.forEach(
        key => this.addEventListener(
          key, this.toEventHandler(key)
        )
      )
    }
  }
}


const inherit = (element, attrs) => {
  return class extends element {
    async connectedCallback() {
      const host = this.getRootNode().host;
      attrs.forEach(attr => {
        if (host.hasAttribute(attr)) {
          this.setAttribute(
            attr, host.getAttribute(attr)
          );
        };
      });
      await super.connectedCallback();
    }
  }
}


export { index }
