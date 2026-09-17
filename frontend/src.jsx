import React from "react";
import { createRoot } from "react-dom/client";
import { motion, MotionConfig, useReducedMotion } from "framer-motion";

function Header() {
  const reduced = useReducedMotion();
  const reveal = (delay) => ({
    initial: reduced ? false : { opacity: 0, y: 12 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: reduced ? 0 : 0.55, delay: reduced ? 0 : delay, ease: [0.22, 1, 0.36, 1] }
  });
  return <MotionConfig reducedMotion="user">
    <header data-motion={reduced ? "reduced" : "enabled"}>
      <motion.div className="halo" aria-hidden="true"
        initial={reduced ? false : { opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: reduced ? 0 : 1.2 }} />
      <motion.div className="eyebrow" {...reveal(0)}>RESEARCH WORKSPACE / 01</motion.div>
      <motion.h1 {...reveal(0.07)}>Inside the allocation signal.</motion.h1>
      <motion.p {...reveal(0.14)}>Explore return direction, allocation groups and the historical signals behind the ENS Data Camp project.</motion.p>
    </header>
  </MotionConfig>;
}

// Streamlit v1 component handshake. Only communicate with this iframe's parent.
const send = (type, payload = {}) => window.parent.postMessage({
  isStreamlitMessage: true, type, ...payload
}, "*");
const root = createRoot(document.getElementById("root"));
let mounted = false;
window.addEventListener("message", event => {
  if (event.source !== window.parent || event.data?.type !== "streamlit:render") return;
  // Stable component key keeps the entrance animation from replaying on filters.
  if (!mounted) {
    root.render(<Header />);
    mounted = true;
  }
});
let previousHeight = 0;
new ResizeObserver(() => {
  const height = Math.ceil(document.getElementById("root").getBoundingClientRect().height);
  if (height !== previousHeight) {
    send("streamlit:setFrameHeight", { height });
    previousHeight = height;
  }
}).observe(document.getElementById("root"));
send("streamlit:componentReady", { apiVersion: 1 });
