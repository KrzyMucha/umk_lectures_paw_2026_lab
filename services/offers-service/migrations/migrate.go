package migrations

import (
	"log"

	"offers-service/models"

	"gorm.io/gorm"
)

func Run(db *gorm.DB) error {
	log.Println("running database migrations...")

	if err := db.AutoMigrate(&models.Offer{}, &models.SuperSeller{}); err != nil {
		return err
	}

	log.Println("database migrations completed")
	return nil
}
