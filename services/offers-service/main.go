package main

import (
	"log"
	"net/http"
	"os"

	"offers-service/handlers"
	"offers-service/repository"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		log.Fatal("DATABASE_URL is required")
	}

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	repo := repository.NewOfferRepository(db)
	offerHandler := handlers.NewOfferHandler(repo)

	r := gin.Default()

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	r.GET("/offers", offerHandler.GetOffers)
	r.POST("/offers", offerHandler.CreateOffer)
	r.GET("/offers-super", offerHandler.GetSuperOffers)
	r.PATCH("/offers-super", offerHandler.AssignSuperSeller)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8082"
	}

	log.Printf("offers-service listening on :%s", port)
	log.Fatal(r.Run(":" + port))
}
