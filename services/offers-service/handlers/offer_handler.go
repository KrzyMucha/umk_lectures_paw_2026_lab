package handlers

import (
	"log"
	"net/http"
	"strings"

	"offers-service/models"

	"github.com/gin-gonic/gin"
)

type OfferRepository interface {
	FindAll(offers *[]models.Offer) error
	FindSuperOffers(offers *[]models.Offer) error
	Create(offer *models.Offer) error
	FindOffer(id int, offer *models.Offer) error
	FindSuperSeller(id int, seller *models.SuperSeller) error
	Save(offer *models.Offer) error
}

type OfferHandler struct {
	repo OfferRepository
}

func NewOfferHandler(repo OfferRepository) *OfferHandler {
	return &OfferHandler{repo: repo}
}

func (h *OfferHandler) GetOffers(c *gin.Context) {
	var offers []models.Offer
	if err := h.repo.FindAll(&offers); err != nil {
		log.Printf("getOffers error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	log.Printf("Offers fetched endpoint=/offers results_count=%d", len(offers))
	c.JSON(http.StatusOK, offers)
}

func (h *OfferHandler) CreateOffer(c *gin.Context) {
	var body struct {
		Title         *string  `json:"title"`
		Description   *string  `json:"description"`
		Price         *float64 `json:"price"`
		SuperSellerID *int     `json:"superSellerId"`
	}

	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON payload"})
		return
	}

	if body.Title == nil || strings.TrimSpace(*body.Title) == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Title is required"})
		return
	}

	if body.Price == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Price must be numeric"})
		return
	}

	offer := models.Offer{
		Title:         strings.TrimSpace(*body.Title),
		Description:   body.Description,
		Price:         *body.Price,
		SuperSellerID: body.SuperSellerID,
	}

	if err := h.repo.Create(&offer); err != nil {
		log.Printf("createOffer error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	c.JSON(http.StatusCreated, offer)
}

func (h *OfferHandler) GetSuperOffers(c *gin.Context) {
	var offers []models.Offer
	if err := h.repo.FindSuperOffers(&offers); err != nil {
		log.Printf("getSuperOffers error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	c.JSON(http.StatusOK, offers)
}

func (h *OfferHandler) AssignSuperSeller(c *gin.Context) {
	var body struct {
		OfferID       *int `json:"offerId"`
		SuperSellerID *int `json:"superSellerId"`
	}

	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON payload"})
		return
	}

	if body.OfferID == nil || body.SuperSellerID == nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "offerId and superSellerId are required (int)"})
		return
	}

	var offer models.Offer
	if err := h.repo.FindOffer(*body.OfferID, &offer); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Offer not found"})
		return
	}

	var seller models.SuperSeller
	if err := h.repo.FindSuperSeller(*body.SuperSellerID, &seller); err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "SuperSeller not found"})
		return
	}

	offer.SuperSellerID = body.SuperSellerID
	if err := h.repo.Save(&offer); err != nil {
		log.Printf("assignSuperSeller error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	c.JSON(http.StatusOK, offer)
}
