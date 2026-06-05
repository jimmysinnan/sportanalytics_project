"use client"
import { useRef, useState } from "react"

interface Props {
  onFile: (file: File) => void
  onClose: () => void
}

export default function PhotoUpload({ onFile, onClose }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [selected, setSelected] = useState<File | null>(null)

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setSelected(file)
    setPreview(URL.createObjectURL(file))
  }

  return (
    <div
      style={{
        position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)",
        display: "flex", alignItems: "flex-end", zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          width: "100%", background: "#17182A",
          borderRadius: "28px 28px 0 0", padding: "12px 20px 40px",
          border: "1px solid rgba(255,255,255,0.07)",
        }}
      >
        <div style={{
          width: 36, height: 4, background: "rgba(255,255,255,0.15)",
          borderRadius: 2, margin: "0 auto 20px",
        }} />
        <h3 style={{ color: "#F2F4FF", fontWeight: 800, marginBottom: 8, fontFamily: "'Outfit', sans-serif" }}>
          Ta photo de joueur
        </h3>
        <p style={{ color: "#7B8098", fontSize: "0.8rem", marginBottom: 20, lineHeight: 1.5, fontFamily: "'Outfit', sans-serif" }}>
          Photo de face, bien éclairée. Elle apparaît sur ta Player Card.
        </p>

        {preview && (
          <div style={{ textAlign: "center", marginBottom: 16 }}>
            <img src={preview} alt="preview" style={{
              width: 120, height: 160, objectFit: "cover",
              borderRadius: 12, border: "2px solid rgba(200,255,87,0.3)",
            }} />
          </div>
        )}

        <input
          ref={inputRef} type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleChange}
          style={{ display: "none" }}
        />

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <button
            onClick={() => inputRef.current?.click()}
            style={{
              width: "100%", background: "#C8FF57", color: "#0E0F18",
              border: "none", borderRadius: 100, padding: "14px",
              fontWeight: 800, fontSize: "0.9rem", cursor: "pointer",
              fontFamily: "'Outfit', sans-serif",
            }}
          >
            {preview ? "Changer la photo" : "📷 Choisir une photo"}
          </button>

          {selected && (
            <button
              onClick={() => { onFile(selected); onClose() }}
              style={{
                width: "100%", background: "rgba(200,255,87,0.15)",
                color: "#C8FF57", border: "1px solid rgba(200,255,87,0.3)",
                borderRadius: 100, padding: "14px",
                fontWeight: 800, fontSize: "0.9rem", cursor: "pointer",
                fontFamily: "'Outfit', sans-serif",
              }}
            >
              Confirmer et enregistrer
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
