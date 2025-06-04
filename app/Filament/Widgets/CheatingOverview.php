<?php

namespace App\Filament\Widgets;

use App\Filament\Resources\CheatingEventResource;
use App\Models\CheatingEvent;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class CheatingOverview extends BaseWidget
{
    protected function getStats(): array
    {
        return [
            Stat::make('students', CheatingEvent::distinct('name')->count('id'))
                ->label('Jumlah siswa')
                ->description('Tidak termasuk siswa yang tidak terdeteksi')
                ->url(CheatingEventResource::getNavigationUrl()),

            Stat::make('cheatings', CheatingEvent::count('id'))
                ->label('Jumlah kecurangan')
                ->description('Termasuk bukti yang belum diverifikasi')
                ->url(CheatingEventResource::getNavigationUrl()),
        ];
    }
}
