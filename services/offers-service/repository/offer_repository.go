package repository

import (
	"offers-service/models"

	"gorm.io/gorm"
)

type OfferRepository struct {
	db *gorm.DB
}

func NewOfferRepository(db *gorm.DB) *OfferRepository {
	return &OfferRepository{db: db}
}

func (r *OfferRepository) FindAll(offers *[]models.Offer) error {
	return r.db.Order("id").Find(offers).Error
}

func (r *OfferRepository) FindSuperOffers(offers *[]models.Offer) error {
	return r.db.Where("super_seller_id IS NOT NULL").Order("id").Find(offers).Error
}

func (r *OfferRepository) Create(offer *models.Offer) error {
	return r.db.Create(offer).Error
}

func (r *OfferRepository) FindOffer(id int, offer *models.Offer) error {
	return r.db.First(offer, id).Error
}

func (r *OfferRepository) FindSuperSeller(id int, seller *models.SuperSeller) error {
	return r.db.First(seller, id).Error
}

func (r *OfferRepository) Save(offer *models.Offer) error {
	return r.db.Save(offer).Error
}
