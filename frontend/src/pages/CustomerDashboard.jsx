import { useState, useEffect } from "react";
import api from "../services/api";
import OrderCard from "../components/OrderCard";

export default function CustomerDashboard() {
  const [orders, setOrders] = useState([]);
  const [restaurants, setRestaurants] = useState([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);
  const [menu, setMenu] = useState([]);
  const [cart, setCart] = useState({});
  const [address, setAddress] = useState("");
  const [placing, setPlacing] = useState(false);
  const [tab, setTab] = useState("order");

  useEffect(() => {
    loadOrders();
    loadRestaurants();
  }, []);

  async function loadOrders() {
    const { data } = await api.get("/orders");
    setOrders(data);
  }

  async function loadRestaurants() {
    const { data } = await api.get("/restaurants");
    setRestaurants(data);
  }

  async function selectRestaurant(restaurant) {
    setSelectedRestaurant(restaurant);
    const { data } = await api.get(`/restaurants/${restaurant.id}/menu`);
    setMenu(data);
    setCart({});
  }

  function updateCart(itemId, delta) {
    setCart((prev) => {
      const qty = (prev[itemId] || 0) + delta;
      if (qty <= 0) {
        const next = { ...prev };
        delete next[itemId];
        return next;
      }
      return { ...prev, [itemId]: qty };
    });
  }

  async function placeOrder() {
    if (!address.trim()) return alert("Enter a delivery address");
    setPlacing(true);

    const items = Object.entries(cart).map(([menu_item_id, quantity]) => ({
      menu_item_id: Number(menu_item_id),
      quantity,
    }));

    try {
      await api.post("/orders", {
        restaurant_id: selectedRestaurant.id,
        items,
        delivery_address: address,
      });
      setCart({});
      setAddress("");
      setSelectedRestaurant(null);
      setTab("orders");
      loadOrders();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to place order");
    } finally {
      setPlacing(false);
    }
  }

  const cartTotal = Object.entries(cart).reduce((sum, [id, qty]) => {
    const item = menu.find((m) => m.id === Number(id));
    return sum + (item ? item.price * qty : 0);
  }, 0);

  return (
    <div className="container">
      <div style={{ display: "flex", gap: 12, marginTop: 24, marginBottom: 20 }}>
        <button
          className={`btn ${tab === "order" ? "btn-primary" : "btn-outline"}`}
          onClick={() => setTab("order")}
        >
          Order Food
        </button>
        <button
          className={`btn ${tab === "orders" ? "btn-primary" : "btn-outline"}`}
          onClick={() => { setTab("orders"); loadOrders(); }}
        >
          My Orders
        </button>
      </div>

      {tab === "order" && (
        <>
          {!selectedRestaurant ? (
            <>
              <h2 className="page-title">Restaurants</h2>
              <div className="grid grid-2">
                {restaurants.map((r) => (
                  <div key={r.id} className="card" style={{ cursor: "pointer" }} onClick={() => selectRestaurant(r)}>
                    <h3>{r.name}</h3>
                    <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
                      {r.cuisine_type || "Various cuisines"} &middot; {r.address || "Order online"}
                    </p>
                  </div>
                ))}
                {restaurants.length === 0 && (
                  <div className="empty-state">No restaurants available yet</div>
                )}
              </div>
            </>
          ) : (
            <>
              <button className="btn btn-outline btn-sm" onClick={() => setSelectedRestaurant(null)}>
                &larr; Back to restaurants
              </button>

              <h2 className="page-title">{selectedRestaurant.name}'s Menu</h2>

              <div className="grid grid-2">
                {menu.map((item) => (
                  <div key={item.id} className="card">
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <div>
                        <h4>{item.name}</h4>
                        <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
                          {item.description || item.category || ""}
                        </p>
                      </div>
                      <span style={{ fontWeight: 700, fontSize: 16 }}>${item.price.toFixed(2)}</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 10 }}>
                      <button className="btn btn-outline btn-sm" onClick={() => updateCart(item.id, -1)}>
                        &minus;
                      </button>
                      <span style={{ fontWeight: 600, minWidth: 20, textAlign: "center" }}>
                        {cart[item.id] || 0}
                      </span>
                      <button className="btn btn-primary btn-sm" onClick={() => updateCart(item.id, 1)}>
                        +
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {Object.keys(cart).length > 0 && (
                <div className="card" style={{ marginTop: 24, position: "sticky", bottom: 20 }}>
                  <h3 style={{ marginBottom: 12 }}>
                    Your Cart &mdash; ${cartTotal.toFixed(2)}
                  </h3>
                  <div className="form-group">
                    <label>Delivery Address</label>
                    <input
                      className="input"
                      placeholder="123 Main St, City"
                      value={address}
                      onChange={(e) => setAddress(e.target.value)}
                    />
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ width: "100%" }}
                    onClick={placeOrder}
                    disabled={placing}
                  >
                    {placing ? "Placing..." : `Place Order ($${cartTotal.toFixed(2)})`}
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}

      {tab === "orders" && (
        <>
          <h2 className="page-title">My Orders</h2>
          <div className="grid grid-2">
            {orders.map((order) => (
              <OrderCard key={order.id} order={order} />
            ))}
          </div>
          {orders.length === 0 && (
            <div className="empty-state">No orders yet. Go ahead and order something!</div>
          )}
        </>
      )}
    </div>
  );
}
