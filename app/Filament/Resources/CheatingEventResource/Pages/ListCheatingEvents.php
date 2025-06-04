<?php

namespace App\Filament\Resources\CheatingEventResource\Pages;

use App\Filament\Resources\CheatingEventResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListCheatingEvents extends ListRecords
{
    protected static string $resource = CheatingEventResource::class;

    protected ?string $subheading = 'Bukti kecurangan selama ujian dapat dilihat di sini. Gunakan pencarian untuk mencari nama siswa.';

    protected function getHeaderActions(): array
    {
        return [
            // Actions\CreateAction::make(),
        ];
    }
}
