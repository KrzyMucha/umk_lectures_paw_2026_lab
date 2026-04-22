package main

import (
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var db *gorm.DB

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

func main() {
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		log.Fatal("DATABASE_URL is required")
	}

	var err error
	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	r := gin.Default()

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	r.GET("/offers", getOffers)
	r.POST("/offers", createOffer)
	r.GET("/offers-super", getSuperOffers)
	r.PATCH("/offers-super", assignSuperSeller)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8082"
	}

	log.Printf("offers-service listening on :%s", port)
	log.Fatal(r.Run(":" + port))
}

func getOffers(c *gin.Context) {
	var offers []Offer
	if err := db.Order("id").Find(&offers).Error; err != nil {
		log.Printf("getOffers error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	log.Printf("Offers fetched endpoint=/offers results_count=%d", len(offers))
	c.JSON(http.StatusOK, offers)
}

func createOffer(c *gin.Context) {
	var body struct {
		Title       *string  `json:"title"`
		Description *string  `json:"description"`
		Price       *float64 `json:"price"`
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

	offer := Offer{
		Title:       strings.TrimSpace(*body.Title),
		Description: body.Description,
		Price:       *body.Price,
	}

	if err := db.Create(&offer).Error; err != nil {
		log.Printf("createOffer error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	c.JSON(http.StatusCreated, offer)
}

func getSuperOffers(c *gin.Context) {
	var offers []Offer
	if err := db.Where("super_seller_id IS NOT NULL").Order("id").Find(&offers).Error; err != nil {
		log.Printf("getSuperOffers error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	c.JSON(http.StatusOK, offers)
}

func assignSuperSeller(c *gin.Context) {
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

	var offer Offer
	if err := db.First(&offer, *body.OfferID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Offer not found"})
		return
	}

	var seller SuperSeller
	if err := db.First(&seller, *body.SuperSellerID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "SuperSeller not found"})
		return
	}

	offer.SuperSellerID = body.SuperSellerID
	if err := db.Save(&offer).Error; err != nil {
		log.Printf("assignSuperSeller error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	c.JSON(http.StatusOK, offer)
}
