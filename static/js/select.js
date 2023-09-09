document.addEventListener("DOMContentLoaded", function () {
 function e(e, t, l) { let n = e.dataset.dselectValue, s = e.closest(`.${t}`).previousElementSibling, o = s.nextElementSibling.querySelector(`.${l}`), i = s.nextElementSibling.querySelector("input"), a = Array.from(s.options); s.multiple ? a.find(e => e.value === n).selected = !0 : s.value = n, o.click(), s.dispatchEvent(new Event("change")), o.focus(), i && (i.value = "") } function t(e, t, l) { let n = e.parentNode.dataset.dselectValue, s = e.closest(`.${t}`).previousElementSibling, o = s.nextElementSibling.querySelector(`.${l}`), i = s.nextElementSibling.querySelector("input"), a = Array.from(s.options); a.find(e => e.value === n).selected = !1, s.dispatchEvent(new Event("change")), o.click(), i && (i.value = "") } function l(e, t, l, n, s) { let o = t.value.toLowerCase().trim(), i = t.nextElementSibling, a = i.querySelectorAll(".dropdown-header"), r = i.querySelectorAll(".dropdown-item"), c = i.nextElementSibling; a.forEach(e => e.classList.add("d-none")), r.forEach(e => { let t = e.textContent.toLowerCase(); if (t.includes(o)) { e.classList.remove("d-none"); let l = e; for (; l = l.previousElementSibling;)if (l.classList.contains("dropdown-header")) { l.classList.remove("d-none"); break } } else e.classList.add("d-none") }); let d = Array.from(r).filter(e => !e.classList.contains("d-none") && !e.hasAttribute("hidden")); if (d.length < 1) { if (c.classList.remove("d-none"), i.classList.add("d-none"), s && (c.innerHTML = `Press Enter to add "<strong>${t.value}</strong>"`, "Enter" === e.key)) { let u = t.closest(`.${l}`).previousElementSibling, p = u.nextElementSibling.querySelector(`.${n}`); u.insertAdjacentHTML("afterbegin", `<option value="${t.value}" selected>${t.value}</option>`), u.dispatchEvent(new Event("change")), t.value = "", t.dispatchEvent(new Event("keyup")), p.click(), p.focus() } } else c.classList.add("d-none"), i.classList.remove("d-none") } function n(e, t) { let l = e.closest(`.${t}`).previousElementSibling; Array.from(l.options).forEach(e => e.selected = !1), l.dispatchEvent(new Event("change")) } let s = document.querySelectorAll(".form-select"); s.forEach(e => {
  !function e(t, l = {}) {
   t.style.display = "none"; let n = "dselect-wrapper", s = "dselect-placeholder", o = "", i = f("search") || l.search || !1, a = f("creatable") || l.creatable || !1, r = f("clearable") || l.clearable || !1, c = t.dataset.dselectMaxHeight || l.maxHeight || "360px", d = t.dataset.dselectSize || l.size || o; d = "" !== d ? ` form-select-${d}` : ""; let u = `form-select${d}`, p = i ? `<input onkeydown="return event.key !== 'Enter'" onkeyup="dselectSearch(event, this, '${n}', '${u}', ${a})" type="text" class="form-control" placeholder="Recherche" autofocus>` : ""; function f(e) { let l = `data-dselect-${e}`; if (!t.hasAttribute(l)) return null; let n = t.getAttribute(l); return "true" === n.toLowerCase() } function m(e) { return "" === e.getAttribute("value") } function v(e, t) {
    if (t) {
     let l = Array.from(e).filter(e => e.selected && !m(e)), o = Array.from(e).filter(e => m(e)), i = []; if (0 === l.length) { let a = o.length ? o[0].textContent : "&nbsp;"; i.push(`<span class="${s}">${a}</span>`) } else for (let r of l) i.push(`<div class="dselect-tag" data-dselect-value="${r.value}">
                                        ${r.text}
                                        <svg onclick="dselectRemoveTag(this, '${n}', '${u}')" class="dselect-tag-remove" width="14" height="14" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                                            <path d="M0 0h24v24H0z" fill="none"/>
                                            <path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z"/>
                                        </svg>
                                    </div>
                                `); return i.join("")
    } { let c = e[e.selectedIndex]; return m(c) ? `<span class="${s}">${c.innerHTML}</span>` : c.innerHTML }
   } function h(e) { let t = e[e.selectedIndex]; return m(t) ? "" : t.textContent } function g(e) { let l = []; for (let s of e) if ("OPTGROUP" === s.tagName) l.push(`<h6 class="dropdown-header">${s.getAttribute("label")}</h6>`); else { let o = m(s) ? " hidden" : "", i = s.selected ? " active" : "", a = t.multiple && s.selected ? " disabled" : "", r = s.value, c = s.textContent; l.push(`<button${o} class="dropdown-item${i}" data-dselect-value="${r}" type="button" onclick="dselectUpdate(this, '${n}', '${u}')" ${a}>${c}</button>`) } return l.join("") } function _() { let e = t.nextElementSibling, l = e.querySelector(`.${u}`), n = e.querySelector(".dselect-items"); l.innerHTML = v(t.options, t.multiple), n.innerHTML = g(t.querySelectorAll("*")), t.multiple || (l.dataset.dselectText = h(t.options)) } t.addEventListener("change", _), function e() {
    let l = t.multiple ? ' data-bs-auto-close="outside"' : "", s = Array.from(t.classList).filter(e => "form-select" !== e && "form-select-sm" !== e && "form-select-lg" !== e).join(" "), o = r && !t.multiple ? `
   <button type="button" class="btn dselect-clear" title="Clear selection" onclick="dselectClear(this, '${n}')">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14" fill="none">
     <path d="M13 1L0.999999 13" stroke-width="2" stroke="currentColor"></path>
     <path d="M1 1L13 13" stroke-width="2" stroke="currentColor"></path>
    </svg>
   </button>
   `: "", i = `
   <div class="dropdown ${n} ${s}">
    <button class="${u} ${!t.multiple && r ? "dselect-clearable" : ""}" data-dselect-text="${!t.multiple && h(t.options)}" type="button" style="text-align: left!important;" data-bs-toggle="dropdown" aria-expanded="false" ${l}>
     ${v(t.options, t.multiple)}
    </button>
    <div class="dropdown-menu w-100">
     <div class="d-flex flex-column">
      ${p}
      <div class="dselect-items" style="max-height:${c};overflow:auto">
       ${g(t.querySelectorAll("*"))}
      </div>
      <div class="dselect-no-results d-none p-2 text-danger">Aucun r\xe9sultat trouv\xe9</div>
     </div>
    </div>
    ${o}
   </div>
   `; t.nextElementSibling && t.nextElementSibling.classList && t.nextElementSibling.classList.contains(n) && t.nextElementSibling.remove(), t.insertAdjacentHTML("afterend", i)
   }(), _()
  }(e, { search: !0 })
 })
});