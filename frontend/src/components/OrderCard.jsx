import { useOrderSocket } from "../hooks/useWebSocket";

export default function OrderCard({ order, actions, onStatusChange }) {
  const { lastMessage, connected } = useOrderSocket(order.id);

  const displayStatus = lastMessage?.status || order.status;

  return (
    <div className="card">
      <div className="order-header">
        <span className="order-id">Order #{order.id}</span>
        <span className={`badge badge-${displayStatus}`}>{displayStatus}</span>
      </div>

      <div className="order-meta">
        {connected && (
          <span>
            <span className="live-dot" />
            Live
          </span>
        )}
        {" · "}
        {order.delivery_address}
      </div>

      {order.items?.length > 0 && (
        <ul className="order-items">
          {order.items.map((item) => (
            <li key={item.id}>
              {item.quantity}x Item #{item.menu_item_id} &mdash; $
              {(item.unit_price * item.quantity).toFixed(2)}
            </li>
          ))}
        </ul>
      )}

      <div className="order-header" style={{ marginTop: 12, marginBottom: 0 }}>
        <span className="order-total">${order.total_amount.toFixed(2)}</span>
        <span className="order-meta" style={{ margin: 0 }}>
          {new Date(order.created_at).toLocaleString()}
        </span>
      </div>

      {actions && (
        <div className="order-actions">
          {actions.map((action) => (
            <button
              key={action.label}
              className={`btn btn-sm ${action.className || "btn-primary"}`}
              onClick={() => onStatusChange(order.id, action.status)}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
