package pubsub

import (
	"context"
	"encoding/json"
	"log"

	gcppubsub "cloud.google.com/go/pubsub/v2"
)

type ServiceLog struct {
	Timestamp string `json:"timestamp"`
	Entity    string `json:"entity"`
	Operation string `json:"operation"`
	Payload   string `json:"payload"`
	Endpoint  string `json:"endpoint"`
}

type Publisher interface {
	Publish(ctx context.Context, msg ServiceLog)
}

type GCPPublisher struct {
	publisher *gcppubsub.Publisher
}

func NewGCPPublisher(ctx context.Context, projectID, topicName string) (*GCPPublisher, error) {
	client, err := gcppubsub.NewClient(ctx, projectID)
	if err != nil {
		return nil, err
	}
	return &GCPPublisher{publisher: client.Publisher(topicName)}, nil
}

func (p *GCPPublisher) Publish(ctx context.Context, msg ServiceLog) {
	data, err := json.Marshal(msg)
	if err != nil {
		log.Printf("pubsub: failed to marshal message: %v", err)
		return
	}
	result := p.publisher.Publish(ctx, &gcppubsub.Message{Data: data})
	go func() {
		if _, err := result.Get(ctx); err != nil {
			log.Printf("pubsub: failed to publish message: %v", err)
		}
	}()
}

type NoopPublisher struct{}

func (NoopPublisher) Publish(context.Context, ServiceLog) {}
