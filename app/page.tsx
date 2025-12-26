export default function Page() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "white",
        color: "black",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      <div style={{ maxWidth: "600px", textAlign: "center" }}>
        <h1 style={{ fontSize: "48px", fontWeight: "bold", marginBottom: "20px" }}>Know Your Rights</h1>

        <p style={{ fontSize: "24px", color: "#555", marginBottom: "40px" }}>
          Unlock the knowledge that could save you thousands
        </p>

        <div
          style={{
            background: "#fef3c7",
            border: "2px solid #fbbf24",
            borderRadius: "8px",
            padding: "30px",
            marginBottom: "20px",
          }}
        >
          <p style={{ fontSize: "14px", fontWeight: "bold", color: "#dc2626", marginBottom: "10px" }}>
            LIMITED TIME: Offer ends January 31, 2025
          </p>
          <p style={{ fontSize: "36px", fontWeight: "bold", marginBottom: "10px" }}>Premium Unlimited - $20</p>
          <p style={{ color: "#666" }}>All 13 Bundles + Lifetime Updates Forever</p>
        </div>

        <a
          href="https://knowyourrights-2.emergent.host"
          style={{
            display: "inline-block",
            background: "black",
            color: "white",
            padding: "16px 40px",
            borderRadius: "8px",
            textDecoration: "none",
            fontSize: "18px",
            fontWeight: "600",
            marginBottom: "20px",
          }}
        >
          Get Access Now
        </a>

        <div
          style={{
            display: "flex",
            gap: "20px",
            justifyContent: "center",
            fontSize: "14px",
            color: "#666",
            marginBottom: "40px",
          }}
        >
          <span>$10 - All 13 Bundles</span>
          <span>$2.99 - Single Bundle</span>
        </div>

        <div style={{ textAlign: "left", fontSize: "18px", lineHeight: "1.8" }}>
          <p>
            <strong>Tenant Rights:</strong> Stop illegal evictions
          </p>
          <p>
            <strong>Worker Rights:</strong> Know your protections
          </p>
          <p>
            <strong>Consumer Rights:</strong> Avoid scams
          </p>
          <p>
            <strong>13 Complete Bundles</strong> covering all your rights
          </p>
        </div>
      </div>
    </div>
  )
}
