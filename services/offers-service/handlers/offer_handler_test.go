package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"offers-service/models"
	"offers-service/pubsub"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"gorm.io/gorm"
)

type MockPublisher struct {
	mock.Mock
}

func (m *MockPublisher) Publish(ctx context.Context, msg pubsub.ServiceLog) {
	m.Called(ctx, msg)
}

type MockDB struct {
	mock.Mock
}

func (m *MockDB) FindAll(offers *[]models.Offer) error {
	args := m.Called(offers)
	if fn, ok := args.Get(0).(func(*[]models.Offer)); ok {
		fn(offers)
	}
	return args.Error(1)
}

func (m *MockDB) FindSuperOffers(offers *[]models.Offer) error {
	args := m.Called(offers)
	if fn, ok := args.Get(0).(func(*[]models.Offer)); ok {
		fn(offers)
	}
	return args.Error(1)
}

func (m *MockDB) Create(offer *models.Offer) error {
	args := m.Called(offer)
	if fn, ok := args.Get(0).(func(*models.Offer)); ok {
		fn(offer)
	}
	return args.Error(1)
}

func (m *MockDB) FindOffer(id int, offer *models.Offer) error {
	args := m.Called(id, offer)
	if fn, ok := args.Get(0).(func(int, *models.Offer)); ok {
		fn(id, offer)
	}
	return args.Error(1)
}

func (m *MockDB) FindSuperSeller(id int, seller *models.SuperSeller) error {
	args := m.Called(id, seller)
	if fn, ok := args.Get(0).(func(int, *models.SuperSeller)); ok {
		fn(id, seller)
	}
	return args.Error(1)
}

func (m *MockDB) Save(offer *models.Offer) error {
	args := m.Called(offer)
	return args.Error(0)
}

func setupRouter(handler *OfferHandler) *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.GET("/offers", handler.GetOffers)
	r.POST("/offers", handler.CreateOffer)
	r.GET("/offers-super", handler.GetSuperOffers)
	r.PATCH("/offers-super", handler.AssignSuperSeller)
	return r
}

// --- GetOffers ---

func TestGetOffers_Empty(t *testing.T) {
	mockDB := new(MockDB)
	mockDB.On("FindAll", mock.Anything).Return(nil, nil)

	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodGet, "/offers", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var offers []models.Offer
	json.Unmarshal(w.Body.Bytes(), &offers)
	assert.Empty(t, offers)
	mockDB.AssertExpectations(t)
}

func TestGetOffers_ReturnsSeedData(t *testing.T) {
	desc := "test desc"
	mockDB := new(MockDB)
	mockDB.On("FindAll", mock.Anything).Return(func(offers *[]models.Offer) {
		*offers = []models.Offer{
			{ID: 1, Title: "Offer A", Description: &desc, Price: 10.0},
			{ID: 2, Title: "Offer B", Price: 20.0},
		}
	}, nil)

	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodGet, "/offers", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var offers []models.Offer
	json.Unmarshal(w.Body.Bytes(), &offers)
	assert.Len(t, offers, 2)
	assert.Equal(t, "Offer A", offers[0].Title)
	mockDB.AssertExpectations(t)
}

func TestGetOffers_DBError(t *testing.T) {
	mockDB := new(MockDB)
	mockDB.On("FindAll", mock.Anything).Return(nil, gorm.ErrInvalidDB)

	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodGet, "/offers", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusInternalServerError, w.Code)
	mockDB.AssertExpectations(t)
}

// --- CreateOffer ---

func TestCreateOffer_Success(t *testing.T) {
	mockDB := new(MockDB)
	mockDB.On("Create", mock.Anything).Return(func(o *models.Offer) {
		o.ID = 1
	}, nil)
	mockPub := new(MockPublisher)
	mockPub.On("Publish", mock.Anything, mock.MatchedBy(func(msg pubsub.ServiceLog) bool {
		return msg.Entity == "offer" && msg.Operation == "CREATE" && msg.Endpoint == "/offers"
	})).Return()

	h := NewOfferHandler(mockDB, mockPub)
	r := setupRouter(h)

	body := `{"title":"New Offer","description":"A nice offer","price":49.99}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPost, "/offers", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)
	var offer models.Offer
	json.Unmarshal(w.Body.Bytes(), &offer)
	assert.Equal(t, "New Offer", offer.Title)
	assert.Equal(t, 49.99, offer.Price)
	assert.Equal(t, 1, offer.ID)
	mockDB.AssertExpectations(t)
	mockPub.AssertExpectations(t)
}

func TestCreateOffer_TrimTitle(t *testing.T) {
	mockDB := new(MockDB)
	mockDB.On("Create", mock.MatchedBy(func(o *models.Offer) bool {
		return o.Title == "Padded Title"
	})).Return(func(o *models.Offer) { o.ID = 1 }, nil)

	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	body := `{"title":"  Padded Title  ","price":5.0}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPost, "/offers", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)
	var offer models.Offer
	json.Unmarshal(w.Body.Bytes(), &offer)
	assert.Equal(t, "Padded Title", offer.Title)
	mockDB.AssertExpectations(t)
}

func TestCreateOffer_MissingTitle(t *testing.T) {
	mockDB := new(MockDB)
	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	body := `{"description":"no title","price":10.0}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPost, "/offers", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestCreateOffer_EmptyTitle(t *testing.T) {
	mockDB := new(MockDB)
	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	body := `{"title":"   ","price":10.0}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPost, "/offers", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestCreateOffer_MissingPrice(t *testing.T) {
	mockDB := new(MockDB)
	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	body := `{"title":"No Price Offer"}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPost, "/offers", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestCreateOffer_InvalidJSON(t *testing.T) {
	mockDB := new(MockDB)
	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPost, "/offers", bytes.NewBufferString("not json"))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestCreateOffer_DBError(t *testing.T) {
	mockDB := new(MockDB)
	mockDB.On("Create", mock.Anything).Return(nil, gorm.ErrInvalidDB)

	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	body := `{"title":"Fail Offer","price":10.0}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPost, "/offers", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusInternalServerError, w.Code)
	mockDB.AssertExpectations(t)
}

// --- GetSuperOffers ---

func TestGetSuperOffers_FiltersCorrectly(t *testing.T) {
	sellerID := 1
	mockDB := new(MockDB)
	mockDB.On("FindSuperOffers", mock.Anything).Return(func(offers *[]models.Offer) {
		*offers = []models.Offer{
			{ID: 2, Title: "Super", Price: 20.0, SuperSellerID: &sellerID},
		}
	}, nil)

	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodGet, "/offers-super", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var offers []models.Offer
	json.Unmarshal(w.Body.Bytes(), &offers)
	assert.Len(t, offers, 1)
	assert.Equal(t, "Super", offers[0].Title)
	mockDB.AssertExpectations(t)
}

func TestGetSuperOffers_EmptyWhenNone(t *testing.T) {
	mockDB := new(MockDB)
	mockDB.On("FindSuperOffers", mock.Anything).Return(nil, nil)

	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodGet, "/offers-super", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var offers []models.Offer
	json.Unmarshal(w.Body.Bytes(), &offers)
	assert.Empty(t, offers)
	mockDB.AssertExpectations(t)
}

// --- AssignSuperSeller ---

func TestAssignSuperSeller_Success(t *testing.T) {
	mockDB := new(MockDB)
	mockDB.On("FindOffer", 1, mock.Anything).Return(func(id int, o *models.Offer) {
		o.ID = 1
		o.Title = "Assignable"
		o.Price = 15.0
	}, nil)
	mockDB.On("FindSuperSeller", 1, mock.Anything).Return(func(id int, s *models.SuperSeller) {
		s.ID = 1
	}, nil)
	mockDB.On("Save", mock.Anything).Return(nil)
	mockPub := new(MockPublisher)
	mockPub.On("Publish", mock.Anything, mock.MatchedBy(func(msg pubsub.ServiceLog) bool {
		return msg.Entity == "offer" && msg.Operation == "UPDATE" && msg.Endpoint == "/offers-super"
	})).Return()

	h := NewOfferHandler(mockDB, mockPub)
	r := setupRouter(h)

	body := `{"offerId":1,"superSellerId":1}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPatch, "/offers-super", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	var offer models.Offer
	json.Unmarshal(w.Body.Bytes(), &offer)
	assert.NotNil(t, offer.SuperSellerID)
	assert.Equal(t, 1, *offer.SuperSellerID)
	mockDB.AssertExpectations(t)
	mockPub.AssertExpectations(t)
}

func TestAssignSuperSeller_OfferNotFound(t *testing.T) {
	mockDB := new(MockDB)
	mockDB.On("FindOffer", 999, mock.Anything).Return(nil, gorm.ErrRecordNotFound)

	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	body := `{"offerId":999,"superSellerId":1}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPatch, "/offers-super", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
	mockDB.AssertExpectations(t)
}

func TestAssignSuperSeller_SellerNotFound(t *testing.T) {
	mockDB := new(MockDB)
	mockDB.On("FindOffer", 1, mock.Anything).Return(func(id int, o *models.Offer) {
		o.ID = 1
		o.Title = "Offer"
		o.Price = 10.0
	}, nil)
	mockDB.On("FindSuperSeller", 999, mock.Anything).Return(nil, gorm.ErrRecordNotFound)

	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	body := `{"offerId":1,"superSellerId":999}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPatch, "/offers-super", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
	mockDB.AssertExpectations(t)
}

func TestAssignSuperSeller_MissingFields(t *testing.T) {
	mockDB := new(MockDB)
	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	body := `{"offerId":1}`
	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPatch, "/offers-super", bytes.NewBufferString(body))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestAssignSuperSeller_InvalidJSON(t *testing.T) {
	mockDB := new(MockDB)
	h := NewOfferHandler(mockDB, pubsub.NoopPublisher{})
	r := setupRouter(h)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest(http.MethodPatch, "/offers-super", bytes.NewBufferString("{bad"))
	req.Header.Set("Content-Type", "application/json")
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}
