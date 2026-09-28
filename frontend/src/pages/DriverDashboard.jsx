import { useState, useEffect } from "react";
import api from "../services/api";
import OrderCard from "../components/OrderCard";

const DRIVER_ACTIONS = {
  ready: [{ label: "Pick Up", status: "assign", className: "btn-primary" }],
  picked_up: [{ label: "On the Way", status: "on_the_way", className: "btn-primary" }],
  on_the_way: [{ label: "Delivered", status: "delivered", className: "btn-success" }],
};

export default function DriverDashboard() {
  const [myOrders, setMyOrders] = useState([]);
  const [availableOrders, setAvailableOrders] = useState([]);
  const [tab, setTab] = useState("available");

  useEffect(() => {
    loadMyOrders();
    loadAvailableOrders();
  }, []);

  async function loadMyOrders() {
    const { data } = await api.get("/orders");
    setMyOrders(data);
  }

  async function loadAvailableOrders() {
    const { data } = await api.get("/orders/available");
    setAvailableOrders(data);
  }

  async function handleAction(orderId, action) {
    if (action === "assign") {
      await api.post(`/orders/${orderId}/assign`);
    } else {
      await api.patch(`/orders/${orderId}/status`, { status: action });
    }
    loadMyOrders();
    loadAvailableOrders();
  }

  async function updateLocation() {
    if (!navigator.geolocation) return alert("Geolocation not supported");

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        await api.post("/orders/driver/location", {
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
        });
      },
      () => alert("Location permission denied")
    );
  }

  const activeDeliveries = myOrders.filter((o) => ["picked_up", "on_the_way"].includes(o.status));
  const completedDeliveries = myOrders.filter((o) => o.status === "delivered");

  return (
    <div className="container">
      <div style={{ display: "flex", gap: 12, marginTop: 24, marginBottom: 20, flexWrap: "wrap" }}>
        <button
          className={`btn ${tab === "available" ? "btn-primary" : "btn-outline"}`}
          onClick={() => { setTab("available"); loadAvailableOrders(); }}
        >
          Available ({availableOrders.length})
        </button>
        <button
          className={`btn ${tab === "active" ? "btn-primary" : "btn-outline"}`}
          onClick={() => { setTab("active"); loadMyOrders(); }}
        >
          My Deliveries ({activeDeliveries.length})
        </button>
        <button
          className={`btn ${tab === "history" ? "btn-primary" : "btn-outline"}`}
          onClick={() => { setTab("history"); loadMyOrders(); }}
        >
          Completed
        </button>
        <button className="btn btn-outline" onClick={updateLocation}>
          Update Location
        </button>
      </div>

      {tab === "available" && (
        <>
          <h2 className="page-title">Available for Pickup</h2>
          <div className="grid grid-2">
            {availableOrders.map((order) => (
              <OrderCard
                key={order.id}
                order={order}
                actions={DRIVER_ACTIONS[order.status]}
                onStatusChange={handleAction}
              />
            ))}
          </div>
          {availableOrders.length === 0 && (
            <div className="empty-state">No orders waiting for pickup</div>
          )}
        </>
      )}

      {tab === "active" && (
        <>
          <h2 className="page-title">Active Deliveries</h2>
          <div className="grid grid-2">
            {activeDeliveries.map((order) => (
              <OrderCard
                key={order.id}
                order={order}
                actions={DRIVER_ACTIONS[order.status]}
                onStatusChange={handleAction}
              />
            ))}
          </div>
          {activeDeliveries.length === 0 && (
            <div className="empty-state">No active deliveries</div>
          )}
        </>
      )}

      {tab === "history" && (
        <>
          <h2 className="page-title">Completed Deliveries</h2>
          <div className="grid grid-2">
            {completedDeliveries.map((order) => (
              <OrderCard key={order.id} order={order} />
            ))}
          </div>
          {completedDeliveries.length === 0 && (
            <div className="empty-state">No completed deliveries yet</div>
          )}
        </>
      )}
    </div>
  );
}
