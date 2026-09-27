import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Register() {
  const [form, setForm] = useState({
    email: "",
    name: "",
    password: "",
    role: "customer",
    phone: "",
    address: "",
    cuisine_type: "",
  });
  const [error, setError] = useState("");
  const { register } = useAuth();
  const navigate = useNavigate();

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const user = await register(form);
      navigate(user.role === "restaurant" ? "/restaurant" : user.role === "driver" ? "/driver" : "/");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420, marginTop: 80 }}>
      <div className="card">
        <h2 style={{ marginBottom: 24 }}>Create account</h2>
        {error && (
          <div style={{ color: "var(--danger)", marginBottom: 16, fontSize: 14 }}>
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>I am a</label>
            <select className="input" value={form.role} onChange={(e) => update("role", e.target.value)}>
              <option value="customer">Customer</option>
              <option value="restaurant">Restaurant</option>
              <option value="driver">Delivery Driver</option>
            </select>
          </div>
          <div className="form-group">
            <label>Name</label>
            <input className="input" value={form.name} onChange={(e) => update("name", e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              className="input"
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              className="input"
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              required
              minLength={6}
            />
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input className="input" value={form.phone} onChange={(e) => update("phone", e.target.value)} />
          </div>

          {form.role === "restaurant" && (
            <>
              <div className="form-group">
                <label>Restaurant Address</label>
                <input className="input" value={form.address} onChange={(e) => update("address", e.target.value)} />
              </div>
              <div className="form-group">
                <label>Cuisine Type</label>
                <input
                  className="input"
                  value={form.cuisine_type}
                  onChange={(e) => update("cuisine_type", e.target.value)}
                  placeholder="e.g. Indian, Italian, Chinese"
                />
              </div>
            </>
          )}

          <button type="submit" className="btn btn-primary" style={{ width: "100%" }}>
            Sign Up
          </button>
        </form>
        <p style={{ textAlign: "center", marginTop: 16, fontSize: 14, color: "var(--text-muted)" }}>
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
}
