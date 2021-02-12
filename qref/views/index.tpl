<html>

<head>
    <title>
        % if aya_spec:
        ({{ aya_spec }})
        % end
        - القرآن
        - {{ arabic_name }}



    </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="static/css/bootstrap.min.css">
    <style>
        @font-face {
            font-family: 'Saleem';
            src: url('static/fonts/PDMS_Saleem_QuranFont.ttf') format('truetype');
            /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
        }

        @font-face {
            font-family: 'Noori';
            src: url('static/fonts/noori.ttf') format('truetype');
            /* Chrome 4+, Firefox 3.5, Opera 10+, Safari 3—5 */
        }

        .ar-num {
            font-family: Arial;
            text-align: right;
            font-size: large;
            direction: rtl;
            unicode-bidi: bidi-override;
        }

        .ar,
        .arabic {
            font-family: 'Saleem';
            text-align: right;
            font-size: 18pt;
        }

        .ur,
        .urdu {
            font-family: Noori, "Jameel Noori Nastaleeq";
            text-align: right;
            font-size: 14pt;
        }

        .en,
        .english {
            font-family: 'Avenir', Helvetica, Arial, sans-serif;
            text-align: left;
            font-size: 12pt;
        }

        .num {
            font-family: 'Saleem';
            font-size: small;
            vertical-align: top;
            text-align: left;

        }

        .content-wrapper {
            padding: 8px;
            padding-top: 65px;
        }

        .main-sidebar {
            position: fixed;
            height: 100vh;
        }

        hr.visible-xs-block {
            width: 100%;
            background-color: rgba(0, 0, 0, 0.17);
            height: 1px;
            border-color: transparent;
        }
    </style>
</head>

<body>
    <div class="container-fluid" style="padding: 20px">
        <div class="row">
            <div class="col-xs-12 ar" style="font-weight: bold; font-size: 24pt; text-align: center;">
                % if aya_spec:
                <span style="font-size: 18pt">
                    ({{ aya_spec }})
                </span>
                % end
                {{ arabic_name }}

            </div>
        </div>
        % for aya in ayas:
        <div class="row">
            <div class="col-xs-12 ar">
                <span class="ar-num">
                    {{ to_arabic_num(aya['aya_number'].split('-')[1]) }}.
                </span>
                {{ aya['texts']['arabic'][ar_tt] }}

            </div>
            % for translation in translations:
            <div class="col-xs-12 {{ translation[0] }}">
                % if translation[0] == 'urdu':
                {{ to_arabic_num(aya['aya_number'].split('-')[1], reverse=False) }}.
                % else:
                {{ aya['aya_number'].split('-')[1] }}.
                % end
                {{ aya['texts'][translation[0]][translation[1]] }}
            </div>
            % end
            <div class="col-xs-12"><br /></div>
        </div>
        % end
    </div>
</body>

</html>