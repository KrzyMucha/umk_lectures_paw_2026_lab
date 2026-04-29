package main

import (
	"log"
	"net/http"
	"os"
	"strings"

	"offers-service/handlers"
	"offers-service/migrations"
	"offers-service/repository"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func openDatabase(dsn string) (*gorm.DB, error) {
	if strings.HasPrefix(dsn, "file:") || strings.HasSuffix(dsn, ".db") {
		return gorm.Open(sqlite.Open(dsn), &gorm.Config{})
	}
	return gorm.Open(postgres.Open(dsn), &gorm.Config{})
}

func main() {
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		log.Fatal("DATABASE_URL is required")
	}

	db, err := openDatabase(dsn)
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	if len(os.Args) > 1 && os.Args[1] == "migrate" {
		if err := migrations.Run(db); err != nil {
			log.Fatalf("migration failed: %v", err)
		}
		log.Println("migration completed successfully")
		return
	}

	if err := migrations.Run(db); err != nil {
		log.Fatalf("startup migration failed: %v", err)
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
