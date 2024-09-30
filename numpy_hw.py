import numpy as np
from scipy.io import wavfile

SAMPLING_RATE = 44100
MAX_AMPLITUDE = 2 ** 13

NOTES = {
    '0': 0, 'e0': 20.60172, 'f0': 21.82676, 'f#0': 23.12465,
    'g0': 24.49971, 'g#0': 25.95654, 'a0': 27.50000, 'a#0': 29.13524,
    'b0': 30.86771, 'c0': 32.70320, 'c#0': 34.64783, 'd0': 36.70810,
    'd#0': 38.89087, 'e1': 41.20344, 'f1': 43.65353, 'f#1': 46.24930,
    'g1': 48.99943, 'g#1': 51.91309, 'a1': 55.00000, 'a#1': 58.27047,
    'b1': 61.73541, 'c1': 65.40639, 'c#1': 69.29566, 'd1': 73.41619,
    'd#1': 77.78175, 'e2': 82.40689, 'f2': 87.30706, 'f#2': 92.49861,
    'g2': 97.99886, 'g#2': 103.8262, 'a2': 110.0000, 'a#2': 116.5409,
    'b2': 123.4708, 'c2': 130.8128, 'c#2': 138.5913, 'd2': 146.8324,
    'd#2': 155.5635, 'e3': 164.8138, 'f3': 174.6141, 'f#3': 184.9972,
    'g3': 195.9977, 'g#3': 207.6523, 'a3': 220.0000, 'a#3': 233.0819,
    'b3': 246.9417, 'c3': 261.6256, 'c#3': 277.1826, 'd3': 293.6648,
    'd#3': 311.1270, 'e4': 329.6276, 'f4': 349.2282, 'f#4': 369.9944,
    'g4': 391.9954, 'g#4': 415.3047, 'a4': 440.0000, 'a#4': 466.1638,
    'b4': 493.8833, 'c4': 523.2511, 'c#4': 554.3653, 'd4': 587.3295,
    'd#4': 622.2540, 'e5': 659.2551, 'f5': 698.4565, 'f#5': 739.9888,
    'g5': 783.9909, 'g#5': 830.6094, 'a5': 880.0000, 'a#5': 932.3275,
    'b5': 987.7666, 'c5': 1046.502, 'c#5': 1108.731, 'd5': 1174.659,
    'd#5': 1244.508, 'e6': 1318.510, 'f6': 1396.913, 'f#6': 1479.978,
    'g6': 1567.982, 'g#6': 1661.219, 'a6': 1760.000, 'a#6': 1864.655,
    'b6': 1975.533, 'c6': 2093.005, 'c#6': 2217.461, 'd6': 2349.318,
    'd#6': 2489.016, 'e7': 2637.020, 'f7': 2793.826, 'f#7': 2959.955,
    'g7': 3135.963, 'g#7': 3322.438, 'a7': 3520.000, 'a#7': 3729.310,
    'b7': 3951.066, 'c7': 4186.009, 'c#7': 4434.922, 'd7': 4698.636,
    'd#7': 4978.032,
}


class SoundWaveFactory:
    def __init__(self):
        self.max_amplitude = MAX_AMPLITUDE
        self.sampling_rate = SAMPLING_RATE

    def get_normed_sin(self, timeline, frequency):
        return self.max_amplitude * np.sin(2 * np.pi * frequency * timeline)

    def create_note(self, note="a4", duration=5, name=None):
        timeline = np.linspace(
            0,
            duration,
            num=self.sampling_rate * duration,
            endpoint=False
        )
        sound_wave = self.get_normed_sin(
            timeline,
            NOTES[note]
        ).astype(np.int16)
        file_name = f"{name}.wav" if name else f"{note}_sin.wav".replace(
            "#",
            "s"
        )
        wavfile.write(file_name, self.sampling_rate, sound_wave)
        return sound_wave

    def read_wave_from_txt(self, file_name):
        return np.loadtxt(file_name)

    def print_wave_details(self, wave):
        print(
            f"Wave Length: {len(wave)}, "
            f"Max Amplitude: {np.max(wave)}, "
            f"Min Amplitude: {np.min(wave)}"
        )

    def normalize_sound_waves(self, *waves):
        min_length = min(len(wave) for wave in waves)
        normalized_waves = [
            wave[:min_length] / np.max(np.abs(wave))
            for wave in waves
        ]
        return normalized_waves

    def save_wave(self, wave, file_name='wave.txt', file_type='TXT'):
        if file_type.upper() == 'WAV':
            wavfile.write(
                file_name.replace('.txt', '.wav'),
                self.sampling_rate, wave.astype(np.int16)
            )
        else:
            np.savetxt(file_name, wave)

    def switch_wave_type(self, wave, wave_type='triangular'):
        if wave_type.lower() == 'triangular':
            scaled_wave = wave / self.max_amplitude
            triangular_wave = 2 * np.abs(2 * scaled_wave - 1) - 1
            return triangular_wave * self.max_amplitude
        elif wave_type.lower() == 'square':
            return np.sign(wave) * self.max_amplitude
        return wave

    def apply_adsr(
            self,
            wave,
            attack_time,
            decay_time,
            sustain_level,
            release_time,
            duration
    ):
        attack_samples = int(attack_time * self.sampling_rate)
        decay_samples = int(decay_time * self.sampling_rate)
        release_samples = int(release_time * self.sampling_rate)
        sustain_time = duration - (attack_time + decay_time + release_time)
        if sustain_time < 0:
            raise ValueError(
                "Duration is too short to accommodate all ADSR phases."
            )

        sustain_samples = int(sustain_time * self.sampling_rate)

        total_samples = len(wave)
        if sum([
            sustain_samples,
            attack_samples,
            decay_samples,
            release_samples
        ]) > total_samples:
            raise ValueError(
                "Duration is too short to accommodate all ADSR phases."
            )

        envelope = np.ones(total_samples)
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        envelope[attack_samples:attack_samples + decay_samples] = np.linspace(
            1, sustain_level, decay_samples
        )
        envelope[
            attack_samples + decay_samples:
            attack_samples + decay_samples + sustain_samples
        ] = sustain_level
        envelope[total_samples - release_samples:] = np.linspace(
            sustain_level, 0, release_samples
        )

        adsr_wave = wave * envelope
        return adsr_wave

    def combine_waves(self, wave1, wave2):
        """Combine two waves by adding them and normalizing the result."""
        min_length = min(len(wave1), len(wave2))
        combined_wave = wave1[:min_length] + wave2[:min_length]
        combined_wave = (
            combined_wave / np.max(np.abs(combined_wave)) * self.max_amplitude
        )
        return combined_wave


if __name__ == "__main__":
    factory = SoundWaveFactory()
    factory.create_note(note="a4", duration=2, name="A4_Note")
    wave_from_txt = factory.read_wave_from_txt("waves.txt")
    factory.print_wave_details(wave_from_txt)
    wave1 = factory.create_note(note="c4", duration=1, name="C4_Note")
    wave2 = factory.create_note(note="e4", duration=1, name="E4_Note")
    normalized_waves = factory.normalize_sound_waves(
        wave_from_txt,
        wave1,
        wave2
    )
    print("Normalized Waves Details:")
    factory.print_wave_details(normalized_waves[0])
    factory.save_wave(normalized_waves[0], "normalized_wave.txt")
    triangular_wave = factory.switch_wave_type(
        normalized_waves[0],
        wave_type="triangular"
    )
    factory.save_wave(triangular_wave, "triangular_wave.wav", file_type='WAV')
    adsr_wave = factory.apply_adsr(
        triangular_wave,
        attack_time=0.2,
        decay_time=0.2,
        sustain_level=0.7,
        release_time=0.3,
        duration=1.0
    )
    factory.save_wave(adsr_wave, "adsr_wave.wav", file_type='WAV')
    combined_wave = factory.combine_waves(wave1, wave2)
    factory.save_wave(combined_wave, "combined_wave.wav", file_type='WAV')
    print("All operations completed successfully.")
