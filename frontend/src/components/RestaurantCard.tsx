import React from 'react';

interface Restaurant {
    id: number;
    name: string;
    cuisine: string;
    disliked_tags: string[];
    latitude: number;
    longitude: number;
    rating: number;
    price_level: number;
    address: string;
}

interface RestaurantCardProps {
    restaurant: Restaurant;
}

const RestaurantCard: React.FC<RestaurantCardProps> = ({ restaurant }) => {
  return (
    <div className="restaurant-card glass-panel" style={{ padding: '16px', margin: '10px 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4 style={{ margin: '0 0 4px 0', fontSize: '1.1rem' }}>{restaurant.name}</h4>
        <span style={{ color: '#fbbf24', fontWeight: 'bold' }}>★ {restaurant.rating}</span>
      </div>
      <p style={{ margin: '0 0 8px 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
        {restaurant.cuisine} • {'$'.repeat(restaurant.price_level)}
      </p>
      <p style={{ margin: '0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
        {restaurant.address}
      </p>
    </div>
  );
};

export default RestaurantCard;