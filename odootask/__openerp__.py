{
    'name': "社区管理",
    'version': '1.0',
    'depends': ['base', "mail"],
    'author': "youfaNi",
    'category': 'Category',
    'description': """
        社区管理
    """,
    # # data files always loaded at installation
    'data': [
        "data/group.xml",
        "workflow/odootask_workflow.xml",
        
        'templates/base.xml',
        'templates/index.xml',
        'templates/search.xml',
        'templates/detail.xml',
        'templates/upload.xml',
        'templates/donator.xml',
        'templates/category_detail.xml',
        'templates/more_category.xml',
        'templates/more_donate.xml',

        'templates/donate_search.xml',

        'templates/pay_donate.xml',
        'templates/statistic.xml',

        'views/catalog.xml',
        'views/community.xml',
        'views/task.xml',
        'views/grant.xml',
        'views/donator.xml',
        'views/donatee.xml',
        'views/category.xml',
        'views/tracktype.xml',

        'views/user.xml',
    ],
    # # data files containing optionally loaded demonstration data
    # 'demo': [
    #     'demo_data.xml',
    # ],
}
