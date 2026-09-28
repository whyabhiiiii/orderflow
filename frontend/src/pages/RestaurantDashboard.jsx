import { useState, useEffect } from "react";
import api from "../services/api";
import OrderCard from "../components/OrderCard";

const STATUS_ACTIONS = {
  placed: [{ label: "Confirm", status: "confirmed", className: "btn-success" }],
  confirmed: [{ label: "Start Preparing", status: "preparing", className: "btn-primary" }],
  preparing: [{ label: "Mark Ready", status: "ready", className: "btn-success" }],
};

export default function RestaurantDashboard() {
  const [orders, setOrders] = useState([]);
  const [tab, setTab] = useState("orders");
  const [menu, setMenu] = useState([]);
  const [newItem, setNewItem] = useState({ name: "", price: "", description: "", category: "" });

  useEffect(() => {
    loadOrders();
  }, []);

  async function loadOrders() {
    const { data } = await api.get("/orders");
    setOrders(data);
  }

  async function loadMenu() {
    const { data } = await api.get("/auth/me");
    const res = await api.get(`/restaurants/${data.id}/menu`);
    setMenu(res.data);
  }

  async function handleStatusChange(orderId, newStatus) {
    await api.patch(`/orders/${orderId}/status`, { status: newStatus });
    loadOrders();
  }

  async function addMenuItem(e) {
    e.preventDefault();
    await api.post("/restaurants/menu", {
      ...newItem,
      price: parseFloat(newItem.price),
    });
    setNewItem({ name: "", price: "", description: "", category: "" });
    loadMenu();
  }

  async function deleteMenuItem(id) {
    await api.delete(`/restaurants/menu/${id}`);
    loadMenu();
  }

  const activeOrders = orders.filter((o) => !["delivered", "cancelled"].includes(o.status));
  const pastOrders = orders.filter((o) => ["delivered", "cancelled"].includes(o.status));

  return (
    <div className="container">
      <div style={{ display: "flex", gap: 12, marginTop: 24, marginBottom: 20 }}>
        <button
          className={`btn ${tab === "orders" ? "btn-primary" : "btn-outline"}`}
          onClick={() => { setTab("orders"); loadOrders(); }}
        >
          Orders ({activeOrders.length})
        </button>
        <button
          className={`btn ${tab === "menu" ? "btn-primary" : "btn-outline"}`}
          onClick={() => { setTab("menu"); loadMenu(); }}
        >
          Menu
        </button>
        <button
          className={`btn ${tab === "history" ? "btn-primary" : "btn-outline"}`}
          onClick={() => { setTab("history"); loadOrders(); }}
        >
          History
        </button>
      </div>

      {tab === "orders" && (
        <>
          <h2 className="page-title">Active Orders</h2>
          <div className="grid grid-2">
            {activeOrders.map((order) => (
              <OrderCard
                key={order.id}
                order={order}
                actions={STATUS_ACTIONS[order.status]}
                onStatusChange={handleStatusChange}
              />
            ))}
          </div>
          {activeOrders.length === 0 && (
            <div className="empty-state">No active orders right now</div>
          )}
        </>
      )}

      {tab === "menu" && (
        <>
          <h2 className="page-title">Manage Menu</h2>

          <div className="card" style={{ marginBottom: 20 }}>
            <h3 style={{ marginBottom: 16 }}>Add Item</h3>
            <form onSubmit={addMenuItem}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="form-group">
                  <label>Name</label>
                  <input
                    className="input"
                    value={newItem.name}
                    onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Price ($)</label>
                  <input
                    className="input"
                    type="number"
                    step="0.01"
                    value={newItem.price}
                    onChange={(e) => setNewItem({ ...newItem, price: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <input
                    className="input"
                    value={newItem.description}
                    onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <input
                    className="input"
                    value={newItem.category}
                    onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                    placeholder="e.g. Starters, Mains, Desserts"
                  />
                </div>
              </div>
              <button type="submit" className="btn btn-primary" style={{ marginTop: 8 }}>
                Add to Menu
              </button>
            </form>
          </div>

          <div className="grid grid-2">
            {menu.map((item) => (
              <div key={item.id} className="card">
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <div>
                    <h4>{item.name}</h4>
                    <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
                      {item.category} &middot; ~{item.prep_time_minutes} min
                    </p>
                  </div>
                  <span style={{ fontWeight: 700 }}>${item.price.toFixed(2)}</span>
                </div>
                <button
                  className="btn btn-outline btn-sm"
                  style={{ marginTop: 10, color: "var(--danger)" }}
                  onClick={() => deleteMenuItem(item.id)}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      {tab === "history" && (
        <>
          <h2 className="page-title">Order History</h2>
          <div className="grid grid-2">
            {pastOrders.map((order) => (
              <OrderCard key={order.id} order={order} />
            ))}
          </div>
          {pastOrders.length === 0 && (
            <div className="empty-state">No past orders</div>
          )}
        </>
      )}
    </div>
  );
}
