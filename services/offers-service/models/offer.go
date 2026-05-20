package models

type Offer struct {
	ID            int     `json:"id" gorm:"primaryKey;autoIncrement"`
	Title         string  `json:"title"`
	Description   *string `json:"description"`
	Price         float64 `json:"price"`
	SuperSellerID *int    `json:"superSellerId" gorm:"column:super_seller_id"`
}

func (Offer) TableName() string {
	return "offer"
}

type SuperSeller struct {
	ID int `gorm:"primaryKey"`
}

func (SuperSeller) TableName() string {
	return "super_seller"
}
