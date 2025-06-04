<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

class CheatingEventTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_create_cheating_event_with_image(): void
    {
        Storage::fake('public');

        $file = UploadedFile::fake()->image('cheating_evidence.jpg');

        $response = $this->postJson('/api/cheating-events', [
            'name' => 'John Doe',
            'image' => $file,
        ]);

        $response->assertStatus(201)
            ->assertJson([
                'success' => true,
                'message' => 'Cheating event recorded successfully',
            ])
            ->assertJsonStructure([
                'success',
                'message',
                'data' => [
                    'id',
                    'name',
                    'image',
                    'image_url',
                    'created_at',
                ],
            ]);

        $this->assertDatabaseHas('cheating_events', [
            'name' => 'John Doe',
        ]);

        /** @disregard */
        Storage::disk('public')->assertExists('cheating-events/' . $file->hashName());
    }

    public function test_validation_fails_with_missing_fields(): void
    {
        $response = $this->postJson('/api/cheating-events', []);

        $response->assertStatus(422)
            ->assertJson([
                'success' => false,
                'message' => 'Validation failed',
            ])
            ->assertJsonValidationErrors(['name', 'image']);
    }

    public function test_validation_fails_with_invalid_image(): void
    {
        $file = UploadedFile::fake()->create('document.pdf', 1000, 'application/pdf');

        $response = $this->postJson('/api/cheating-events', [
            'name' => 'John Doe',
            'image' => $file,
        ]);

        $response->assertStatus(422)
            ->assertJsonValidationErrors(['image']);
    }
}
