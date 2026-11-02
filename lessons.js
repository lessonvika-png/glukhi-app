// Дані курсу «Міст».
// Щоб додати відео до слова — заповни youtube (ID відео з YouTube, напр. "dQw4w9WgXcQ")
// або video (пряме посилання на .mp4). Поки обидва порожні — показується заглушка.
// opys — коротка підказка, як виконується жест (необов'язково).

const WORDS = {
    pryvit:         { text: 'Привіт',       youtube: 'FM54qigsNRs', video: '', opys: '' },
    dobryi_den:     { text: 'Добрий день',  youtube: 'TClTCmaEw_s', video: '', opys: '' },
    diakuiu:        { text: 'Дякую',        youtube: 'hwLI5Z9BFGE', video: '', opys: '' },
    bud_laska:      { text: 'Будь ласка',   youtube: '_3DM9Tm6fxc', video: '', opys: '' },
    do_pobachennia: { text: 'До побачення', youtube: 'i4yaMEGvd-E', video: '', opys: '' },

    // Урок 2 · Родина
    mama:   { text: 'Мама',   youtube: '', video: '', opys: '' },
    tato:   { text: 'Тато',   youtube: '', video: '', opys: '' },
    brat:   { text: 'Брат',   youtube: '', video: '', opys: '' },
    sestra: { text: 'Сестра', youtube: '', video: '', opys: '' },
};

// Типи кроків:
//   learn          — показати жест і слово (вивчення)
//   video_to_word  — показано жест, обрати правильне слово
//   word_to_video  — показано слово, обрати правильний жест
// Заплановано на пізніші уроки:
//   sentence_to_text — речення жестами → обрати/зібрати переклад
//   text_to_sentence — речення текстом → скласти з карток-жестів

const LESSONS = {
    1: {
        title: 'Привітання',
        subtitle: 'Привіт, добрий день, дякую, будь ласка, до побачення',
        demo: true,
        steps: [
            { type: 'learn', word: 'pryvit' },
            { type: 'learn', word: 'dobryi_den' },
            { type: 'video_to_word', word: 'pryvit' },
            { type: 'learn', word: 'diakuiu' },
            { type: 'word_to_video', word: 'dobryi_den' },
            { type: 'learn', word: 'bud_laska' },
            { type: 'video_to_word', word: 'diakuiu' },
            { type: 'learn', word: 'do_pobachennia' },
            { type: 'word_to_video', word: 'bud_laska' },
            { type: 'video_to_word', word: 'do_pobachennia' },
            { type: 'word_to_video', word: 'diakuiu' },
            { type: 'video_to_word', word: 'dobryi_den' },
        ],
    },
    2: {
        title: 'Родина',
        subtitle: 'Мама, тато, брат, сестра',
        steps: [
            { type: 'learn', word: 'mama' },
            { type: 'learn', word: 'tato' },
            { type: 'video_to_word', word: 'mama' },
            { type: 'learn', word: 'brat' },
            { type: 'learn', word: 'sestra' },
            { type: 'word_to_video', word: 'tato' },
            { type: 'video_to_word', word: 'sestra' },
            { type: 'word_to_video', word: 'brat' },
        ],
    },
};
