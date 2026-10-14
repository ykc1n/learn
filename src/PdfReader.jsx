import React, {useState, useEffect, useRef} from 'react';

export function PdfReader({initialPage=1,version,onPage,errorHandler,url='/api/c-pdf'}) {
  const [doc,setDoc]=useState(null),[page,setPage]=useState(initialPage),[draft,setDraft]=useState(initialPage),[status,setStatus]=useState('Opening your PDF…'),[zoom,setZoom]=useState(1),[text,setText]=useState(''),[showText,setShowText]=useState(false);
  const canvas=useRef(),container=useRef(),renderTask=useRef(null);
  useEffect(()=>{
    let stopped=false,loading;
    (async()=>{
      try {
        const modulePath='/pdfjs/pdf.mjs';
        const pdf=await import(/* @vite-ignore */ modulePath);
        pdf.GlobalWorkerOptions.workerSrc='/pdfjs/pdf.worker.mjs';
        loading=pdf.getDocument({url,cMapUrl:'/pdfjs/cmaps/',cMapPacked:true,standardFontDataUrl:'/pdfjs/standard_fonts/',wasmUrl:'/pdfjs/wasm/',isEvalSupported:false});
        const file=await loading.promise;
        if(stopped){await file.destroy();return;}
        const p=Math.max(1,Math.min(initialPage,file.numPages));
        setDoc(file);setPage(p);setDraft(p);setStatus('');
      } catch(e) {if(!stopped){setStatus('Unable to open this PDF. Try importing a valid, unencrypted PDF.');errorHandler(e.message);}}
    })();
    return()=>{stopped=true;renderTask.current?.cancel();loading?.destroy();};
  },[version,url]);
  useEffect(()=>{
    if(!doc)return;
    let stopped=false;
    (async()=>{
      try {
        setStatus('Rendering page…');
        renderTask.current?.cancel();
        const pdfPage=await doc.getPage(page);
        if(stopped)return;
        const unscaled=pdfPage.getViewport({scale:1});
        const width=Math.min(container.current?.clientWidth||650,950)-24;
        const viewport=pdfPage.getViewport({scale:width/unscaled.width*zoom});
        const pixelRatio=Math.min(window.devicePixelRatio||1,2);
        const target=canvas.current;
        target.width=Math.floor(viewport.width*pixelRatio);target.height=Math.floor(viewport.height*pixelRatio);
        target.style.width=viewport.width+'px';target.style.height=viewport.height+'px';
        renderTask.current=pdfPage.render({canvasContext:target.getContext('2d'),viewport,transform:pixelRatio===1?null:[pixelRatio,0,0,pixelRatio,0,0]});
        await renderTask.current.promise;
        const content=await pdfPage.getTextContent();
        if(stopped)return;
        setText(content.items.map(item=>item.str+(item.hasEOL?'\n':' ')).join(''));setStatus('');
      } catch(e) {if(!stopped&&e.name!=='RenderingCancelledException'){setStatus('This page could not be rendered.');errorHandler(e.message);}}
    })();
    return()=>{stopped=true;renderTask.current?.cancel();};
  },[doc,page,zoom]);
  const change=next=>{if(!doc)return;const p=Math.max(1,Math.min(doc.numPages,next));setPage(p);setDraft(p);onPage(p);};
  return <div className="pdf-reader" ref={container}>
    <div className="pdf-tools"><button className="secondary compact" disabled={!doc||page<=1} onClick={()=>change(page-1)}>← Previous</button><label>Page <input aria-label="PDF page" type="number" min="1" max={doc?.numPages||10000} value={draft} onChange={e=>setDraft(e.target.value)} onKeyDown={e=>{if(e.key==='Enter')change(Number(draft)||1);}}/></label><span>of {doc?.numPages||'…'}</span><button className="secondary compact" disabled={!doc} onClick={()=>change(Number(draft)||1)}>Go</button><button className="secondary compact" disabled={!doc||page>=doc.numPages} onClick={()=>change(page+1)}>Next →</button><label className="zoom-control">Zoom <select aria-label="PDF zoom" value={zoom} onChange={e=>setZoom(Number(e.target.value))}><option value={1}>Fit width</option><option value={1.25}>125%</option><option value={1.5}>150%</option></select></label></div>
    {status&&<p className="pdf-status" role="status">{status}</p>}
    <div className="pdf-canvas"><canvas ref={canvas} aria-label={'Book PDF page '+page}/></div>
    <div className="pdf-tools"><button className="text-button" disabled={!doc} onClick={()=>setShowText(!showText)}>{showText?'Hide page text':'Show selectable page text'}</button><a href={url+'#page='+page} target="_blank" rel="noreferrer">Open original PDF ↗</a></div>
    {showText&&<pre className="pdf-selectable-text">{text||'This page has no embedded text. It may be a scanned image.'}</pre>}
    <p className="muted">Page numbers refer to PDF pages, which may differ from the printed page numbers. Your chosen page is saved across devices.</p>
  </div>;
}
